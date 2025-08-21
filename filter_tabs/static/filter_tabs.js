// Progressive enhancement for keyboard navigation
// This file ensures proper keyboard navigation while maintaining CSS-only fallback

(function() {
    'use strict';
    
    // Only enhance if the extension is present
    if (!document.querySelector('.sft-container')) return;
    
    function initTabKeyboardNavigation() {
        const containers = document.querySelectorAll('.sft-container');
        
        containers.forEach(container => {
            const tabBar = container.querySelector('.sft-tab-bar');
            if (!tabBar) return;
            
            const radios = tabBar.querySelectorAll('input[type="radio"]');
            const labels = tabBar.querySelectorAll('label');
            
            if (radios.length === 0 || labels.length === 0) return;
            
            // Make labels focusable for keyboard navigation
            labels.forEach(label => {
                if (!label.hasAttribute('tabindex')) {
                    label.setAttribute('tabindex', '0');
                }
            });
            
            // Handle keyboard navigation on labels
            labels.forEach((label, index) => {
                label.addEventListener('keydown', (event) => {
                    let targetIndex = index;
                    let handled = false;
                    
                    switch (event.key) {
                        case 'ArrowRight':
                            event.preventDefault();
                            targetIndex = (index + 1) % labels.length;
                            handled = true;
                            break;
                            
                        case 'ArrowLeft':
                            event.preventDefault();
                            targetIndex = (index - 1 + labels.length) % labels.length;
                            handled = true;
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
                            // Activate the associated radio button
                            event.preventDefault();
                            if (radios[index]) {
                                radios[index].checked = true;
                                radios[index].dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            return;
                            
                        default:
                            return;
                    }
                    
                    if (handled) {
                        // Move focus to target label and activate its radio
                        labels[targetIndex].focus();
                        if (radios[targetIndex]) {
                            radios[targetIndex].checked = true;
                            radios[targetIndex].dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                });
            });
            
            // Optional: Announce tab changes for screen readers
            if (window.config && window.config.filter_tabs_announce_changes !== false) {
                radios.forEach((radio, index) => {
                    radio.addEventListener('change', () => {
                        if (radio.checked && labels[index]) {
                            announceTabChange(labels[index].textContent.trim());
                        }
                    });
                });
            }
        });
    }
    
    function announceTabChange(tabName) {
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
