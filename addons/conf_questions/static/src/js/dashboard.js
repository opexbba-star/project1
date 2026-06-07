(function () {
    'use strict';

    const body = document.body;
    const eventId = body.dataset.eventId;
    const publicUrl = body.dataset.publicUrl;

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

    function esc(str) {
        const d = document.createElement('div');
        d.textContent = str;
        return d.innerHTML;
    }

    function pendingCard(q) {
        return (
            '<div class="question-card pending" data-id="' + q.id + '">' +
            '  <div class="question-header">' +
            '    <span class="question-submitter">' + esc(q.name) + '</span>' +
            '    <span class="question-time">' + esc(q.time) + '</span>' +
            '  </div>' +
            '  <div class="question-text">' + esc(q.text) + '</div>' +
            '  <div class="question-actions">' +
            '    <button class="btn-lu" onclick="dashboard.markRead(' + q.id + ')">&#x2705; Lu</button>' +
            '    <button class="btn-skip" onclick="dashboard.skipQ(' + q.id + ')">&#x23ED; Skip</button>' +
            '    <button class="btn-supp" onclick="dashboard.deleteQ(' + q.id + ')">&#x1F5D1; Supp</button>' +
            '  </div>' +
            '</div>'
        );
    }

    function historyCard(q) {
        return (
            '<div class="question-card history" data-id="' + q.id + '">' +
            '  <div class="question-header">' +
            '    <span class="question-submitter">' + esc(q.name) + '</span>' +
            '    <span class="question-time treated">Trait&#233;e &#224; ' + esc(q.time) + '</span>' +
            '  </div>' +
            '  <div class="question-text">' + esc(q.text) + '</div>' +
            '  <div class="question-actions">' +
            '    <button class="btn-delete-history" onclick="dashboard.deleteQ(' + q.id + ')">Supprimer</button>' +
            '  </div>' +
            '</div>'
        );
    }

    function refresh() {
        jsonRpc('/conf/dashboard/' + eventId + '/data').then(function (data) {
            if (!data) return;

            document.getElementById('stat-pending').textContent = data.pending_count;
            document.getElementById('stat-history').textContent = data.read_count;
            document.getElementById('stat-total').textContent = data.total;
            document.getElementById('queue-title').textContent =
                'File d\'attente (' + data.pending.length + ')';
            document.getElementById('history-title').textContent =
                'Historique (' + data.history.length + ')';

            const queueEl = document.getElementById('queue-container');
            queueEl.innerHTML = data.pending.length
                ? data.pending.map(pendingCard).join('')
                : '<p class="no-questions">Aucune question en attente</p>';

            const historyEl = document.getElementById('history-container');
            historyEl.innerHTML = data.history.length
                ? data.history.map(historyCard).join('')
                : '<p class="no-questions">Aucune question dans l\'historique</p>';

            const closeBtn = document.getElementById('close-btn');
            if (closeBtn && data.event_status === 'closed') {
                closeBtn.style.display = 'none';
            }
        }).catch(function (e) { console.error('Dashboard refresh error:', e); });
    }

    window.dashboard = {
        markRead: function (qId) {
            jsonRpc('/conf/question/' + qId + '/read').then(refresh);
        },
        skipQ: function (qId) {
            jsonRpc('/conf/question/' + qId + '/skip').then(refresh);
        },
        deleteQ: function (qId) {
            jsonRpc('/conf/question/' + qId + '/delete').then(refresh);
        },
    };

    window.closeEvent = function () {
        if (confirm('Êtes-vous sûr de vouloir clôturer cet événement ?')) {
            jsonRpc('/conf/event/' + eventId + '/close').then(function () {
                window.location.reload();
            });
        }
    };

    window.setLive = function () {
        jsonRpc('/conf/event/' + eventId + '/live').then(function () {
            window.location.reload();
        });
    };

    window.copyShareLink = function () {
        if (!publicUrl) return;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(publicUrl).then(function () {
                alert('Lien copié !\n' + publicUrl);
            });
        } else {
            prompt('Copiez ce lien :', publicUrl);
        }
    };

    // Initial render + 5s polling
    refresh();
    setInterval(refresh, 5000);
})();
