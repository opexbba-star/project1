(function () {
    'use strict';

    function jsonRpc(url, params) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                id: Date.now(),
                params: params || {},
            }),
        })
            .then(function (r) { return r.json(); })
            .then(function (r) { return r.result; });
    }

    window.openNewEventModal = function () {
        document.getElementById('new-event-modal').style.display = 'flex';
    };

    window.closeNewEventModal = function () {
        document.getElementById('new-event-modal').style.display = 'none';
    };

    window.deleteEvent = function (eventId) {
        if (confirm('Supprimer cet événement ? Cette action est irréversible.')) {
            jsonRpc('/conf/event/' + eventId + '/delete').then(function () {
                window.location.reload();
            });
        }
    };

    document.addEventListener('DOMContentLoaded', function () {
        const modal = document.getElementById('new-event-modal');
        if (modal) {
            modal.addEventListener('click', function (e) {
                if (e.target === modal) {
                    closeNewEventModal();
                }
            });
        }
    });
})();
