/** @odoo-module **/
/**
 * CEO Roadshow SBA 2026 — Frontend JavaScript
 * Uses a safe init pattern: works whether DOM is already loaded or not.
 * Uses inline style.display for tab switching (immune to CSS overrides).
 */

function crsInit() {

    // ── Day tabs ─────────────────────────────────────────────────
    var day1 = document.getElementById('crs-day1');
    var day2 = document.getElementById('crs-day2');
    var tab1 = document.getElementById('crs-tab1');
    var tab2 = document.getElementById('crs-tab2');

    function switchDay(day) {
        if (day1) day1.style.display = (day === 1) ? '' : 'none';
        if (day2) day2.style.display = (day === 2) ? '' : 'none';
        if (tab1) tab1.classList.toggle('active', day === 1);
        if (tab2) tab2.classList.toggle('active', day === 2);
    }

    // Force Day 1 as default immediately (overrides any CSS/class issue)
    switchDay(1);

    if (tab1) tab1.addEventListener('click', function () { switchDay(1); });
    if (tab2) tab2.addEventListener('click', function () { switchDay(2); });

    // ── Countdown ────────────────────────────────────────────────
    function updateCountdown() {
        var target = new Date('2026-05-20T09:00:00').getTime();
        var now    = Date.now();
        var diff   = target - now;
        var el     = document.getElementById('crs-countdown');
        if (!el) return;
        if (diff <= 0) {
            el.innerHTML = '<div class="crs-countdown-cell"><p class="crs-countdown-value">\uD83C\uDF89</p><p class="crs-countdown-label">En cours</p></div>';
            return;
        }
        var d = Math.floor(diff / 86400000);
        var h = Math.floor((diff % 86400000) / 3600000);
        var m = Math.floor((diff % 3600000) / 60000);
        el.innerHTML = [
            [String(d).padStart(2, '0'), 'jours'],
            [String(h).padStart(2, '0'), 'heures'],
            [String(m).padStart(2, '0'), 'minutes'],
        ].map(function (pair) {
            return '<div class="crs-countdown-cell"><p class="crs-countdown-value">' + pair[0] +
                   '</p><p class="crs-countdown-label">' + pair[1] + '</p></div>';
        }).join('');
    }
    updateCountdown();
    setInterval(updateCountdown, 30000);

    // ── FAQ accordion ────────────────────────────────────────────
    document.querySelectorAll('.crs-faq-question').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var item   = btn.closest('.crs-faq-item');
            var isOpen = item.classList.contains('open');
            document.querySelectorAll('.crs-faq-item.open').forEach(function (el) {
                el.classList.remove('open');
            });
            if (!isOpen) item.classList.add('open');
        });
    });

    // ── Documents dropdown ────────────────────────────────────────
    document.querySelectorAll('.ceo-tab-button').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            var container = btn.closest('.ceo-dropdown-container');
            var menu = container && container.querySelector('.ceo-dropdown-list');
            if (menu) menu.classList.toggle('show');
        });
    });
    document.addEventListener('click', function () {
        document.querySelectorAll('.ceo-dropdown-list.show').forEach(function (menu) {
            menu.classList.remove('show');
        });
    });

    // ── Scroll reveal ─────────────────────────────────────────────
    if (typeof IntersectionObserver !== 'undefined') {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('.crs-reveal').forEach(function (el) {
            observer.observe(el);
        });
    } else {
        // Fallback: show all immediately
        document.querySelectorAll('.crs-reveal').forEach(function (el) {
            el.classList.add('visible');
        });
    }
}

// ── Safe init: works whether DOM is already loaded or not ────────
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', crsInit);
} else {
    crsInit();
}
