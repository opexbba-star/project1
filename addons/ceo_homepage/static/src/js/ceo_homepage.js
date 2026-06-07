/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CeoHomepageReveal = publicWidget.Widget.extend({
    selector: '.chp-wrap',
    
    start: function () {
        this._super.apply(this, arguments);
        this._initReveal();
    },

    _initReveal: function () {
        const revealElements = this.el.querySelectorAll('.chp-reveal');
        
        if (typeof IntersectionObserver !== 'undefined') {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });

            revealElements.forEach(el => {
                observer.observe(el);
            });
        } else {
            // Fallback
            revealElements.forEach(el => {
                el.classList.add('visible');
            });
        }

        // Safety timeout: if after 2 seconds nothing is visible, force it
        // (This handles cases where the observer might fail or elements are already in view but didn't trigger)
        setTimeout(() => {
            revealElements.forEach(el => {
                if (!el.classList.contains('visible')) {
                    el.classList.add('visible');
                }
            });
        }, 2000);
    }
});
