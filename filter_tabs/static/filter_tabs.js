// Progressive enhancement for keyboard navigation and accessibility
// This file ensures proper keyboard navigation while maintaining CSS-only fallback

(function() {
    'use strict';
    
    // Only enhance if the extension is present
    if (!document.querySelector('.sft-container')) return;
    
    function initTabKeyboardNavigation() {
        const tablists = document.querySelectorAll('.sft-tab-bar[role="tablist"]');
        
        tablists.forEach(tablist => {
            const labels = tablist.querySelectorAll('label[role="tab"]');
            const radios = tablist.querySelectorAll('input[type="radio"]');
            
            if (labels.length === 0 || radios.length === 0) return;
            
            // Create a mapping between labels and their associated radio buttons
            const labelToRadio = new Map();
            labels.forEach((label, index) => {
                if (radios[index]) {
                    labelToRadio.set(label, radios[index]);
                }
            });
            
            // Set up initial tabindex based on checked radio
            updateTabIndexBasedOnCheckedRadio(labels, radios);
            
            // Handle keyboard navigation
            tablist.addEventListener('keydown', (event) => {
                const currentLabel = event.target.closest('label[role="tab"]');
                if (!currentLabel) return;
                
                const labelArray = Array.from(labels);
                const currentIndex = labelArray.indexOf(currentLabel);
                if (currentIndex === -1) return;
                
                let targetIndex = currentIndex;
                let handled = false;
                
                switch (event.key) {
                    case 'ArrowRight':
                        event.preventDefault();
                        targetIndex = (currentIndex + 1) % labels.length;
                        handled = true;
                        break;
                        
                    case 'ArrowLeft':
                        event.preventDefault();
                        targetIndex = (currentIndex - 1 + labels.length) % labels.length;
                        handled = true;
                        break;
                        
                    case 'ArrowDown':
                        // Only handle if orientation is vertical (not in this implementation)
                        if (tablist.getAttribute('aria-orientation') === 'vertical') {
                            event.preventDefault();
                            targetIndex = (currentIndex + 1) % labels.length;
                            handled = true;
                        }
                        break;
                        
                    case 'ArrowUp':
                        // Only handle if orientation is vertical (not in this implementation)
                        if (tablist.getAttribute('aria-orientation') === 'vertical') {
                            event.preventDefault();
                            targetIndex = (currentIndex - 1 + labels.length) % labels.length;
                            handled = true;
                        }
                        break;
                        
                    case 'Home':
                        event.preventDefault();
                        targetIndex = 0;
                        handled = true;
                        break;
                        
                    case 'End':
                        event.preventDefault();
                        targetIndex = labels.length - 1;
                        handled = true;
                        break;
                        
                    case 'Enter':
                    case ' ':
                        // These keys should activate the current tab if it's not already active
                        event.preventDefault();
                        const currentRadio = labelToRadio.get(currentLabel);
                        if (currentRadio && !currentRadio.checked) {
                            activateTab(currentLabel, currentRadio, labels, labelToRadio);
                        }
                        return;
                        
                    default:
                        return;
                }
                
                if (handled) {
                    // Move focus and activate the target tab
                    const targetLabel = labels[targetIndex];
                    const targetRadio = labelToRadio.get(targetLabel);
                    
                    if (targetLabel && targetRadio) {
                        targetLabel.focus();
                        activateTab(targetLabel, targetRadio, labels, labelToRadio);
                    }
                }
            });
            
            // Handle click events to maintain ARIA consistency
            labels.forEach(label => {
                label.addEventListener('click', (event) => {
                    const radio = labelToRadio.get(label);
                    if (radio) {
                        // The browser will handle the radio check, we just update ARIA
                        setTimeout(() => {
                            updateAriaStates(labels, labelToRadio);
                            updateTabIndexBasedOnCheckedRadio(labels, radios);
                        }, 0);
                    }
                });
                
                // Ensure labels are focusable
                if (!label.hasAttribute('tabindex')) {
                    label.setAttribute('tabindex', '-1');
                }
            });
            
            // Handle radio change events (for when changed programmatically or via label click)
            radios.forEach(radio => {
                radio.addEventListener('change', () => {
                    if (radio.checked) {
                        updateAriaStates(labels, labelToRadio);
                        updateTabIndexBasedOnCheckedRadio(labels, radios);
                        announceTabChange(radio);
                    }
                });
            });
        });
    }
    
    function activateTab(targetLabel, targetRadio, allLabels, labelToRadio) {
        // Check the radio button (this triggers the CSS to show the panel)
        targetRadio.checked = true;
        
        // Update ARIA states for all labels
        updateAriaStates(allLabels, labelToRadio);
        
        // Update tabindex for keyboard navigation
        allLabels.forEach(label => {
            if (label === targetLabel) {
                label.setAttribute('tabindex', '0');
            } else {
                label.setAttribute('tabindex', '-1');
            }
        });
        
        // Announce the change to screen readers
        announceTabChange(targetRadio);
        
        // Trigger change event for any other listeners
        const changeEvent = new Event('change', { bubbles: true });
        targetRadio.dispatchEvent(changeEvent);
    }
    
    function updateAriaStates(labels, labelToRadio) {
        labels.forEach(label => {
            const radio = labelToRadio.get(label);
            if (radio) {
                const isSelected = radio.checked;
                label.setAttribute('aria-selected', isSelected ? 'true' : 'false');
            }
        });
    }
    
    function updateTabIndexBasedOnCheckedRadio(labels, radios) {
        // Find which radio is checked
        let checkedIndex = -1;
        radios.forEach((radio, index) => {
            if (radio.checked) {
                checkedIndex = index;
            }
        });
        
        // If no radio is checked, make the first one focusable
        if (checkedIndex === -1) {
            checkedIndex = 0;
        }
        
        // Update tabindex on labels
        labels.forEach((label, index) => {
            if (index === checkedIndex) {
                label.setAttribute('tabindex', '0');
            } else {
                label.setAttribute('tabindex', '-1');
            }
        });
    }
    
    function announceTabChange(radio) {
        // Find the associated label for this radio
        const label = document.querySelector(`label[for="${radio.id}"]`);
        if (!label) return;
        
        const tabName = label.textContent.trim();
        const panelId = label.getAttribute('aria-controls');
        
        // Create or update live region for screen reader announcements
        let liveRegion = document.getElementById('tab-live-region');
        if (!liveRegion) {
            liveRegion = document.createElement('div');
            liveRegion.id = 'tab-live-region';
            liveRegion.setAttribute('role', 'status');
            liveRegion.setAttribute('aria-live', 'polite');
            liveRegion.setAttribute('aria-atomic', 'true');
            liveRegion.style.position = 'absolute';
            liveRegion.style.left = '-10000px';
            liveRegion.style.width = '1px';
            liveRegion.style.height = '1px';
            liveRegion.style.overflow = 'hidden';
            document.body.appendChild(liveRegion);
        }
        
        // Update the announcement
        liveRegion.textContent = `${tabName} tab selected`;
        
        // Clear the announcement after a short delay
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTabKeyboardNavigation);
    } else {
        initTabKeyboardNavigation();
    }
})();
