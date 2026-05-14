/** @odoo-module **/

function formatRemaining(diffMs) {
    if (diffMs <= 0) return { text: 'EXPIRED', expired: true };
    const days = Math.floor(diffMs / 86400000);
    const hours = Math.floor((diffMs % 86400000) / 3600000);
    const mins = Math.floor((diffMs % 3600000) / 60000);
    if (days > 0) return { text: days + 'd ' + hours + 'h', expired: false };
    if (hours > 0) return { text: hours + 'h ' + mins + 'm', expired: false };
    return { text: mins + 'm', expired: false, urgent: true };
}

function setupCountdown(el) {
    if (!el.dataset.deadline) return;
    const deadline = new Date(el.dataset.deadline.replace(' ', 'T') + 'Z');

    function tick() {
        const r = formatRemaining(deadline - new Date());
        el.textContent = r.text;
        if (r.expired) el.classList.add('text-danger', 'fw-bold');
        if (r.urgent) el.classList.add('text-danger', 'fw-bold');
    }
    tick();
    setInterval(tick, 60000);
}

function startAll() {
    // Multiple countdowns on portal page
    document.querySelectorAll('.bb_countdown').forEach(setupCountdown);
    // Legacy single-id countdown (kept for safety, can be removed later)
    const single = document.getElementById('invoice_deadline_countdown');
    if (single && !single.classList.contains('bb_countdown')) {
        setupCountdown(single);
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startAll);
} else {
    startAll();
}
