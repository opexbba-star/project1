/** @odoo-module **/

/*
 * Backend Live Q&A — auto-refresh widget
 *
 * Polls the current event.track form record every POLL_INTERVAL_MS while
 * the Q&A is active, so moderators see new participant submissions without
 * manually pressing F5. Pauses automatically when the user has unsaved
 * edits to avoid clobbering their work.
 *
 * Registered as a view widget; placed in the Live Q&A tab of the
 * event.track form view via `<widget name="qa_auto_refresh"/>`.
 */

import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

const POLL_INTERVAL_MS = 10000;

class QaAutoRefresh extends Component {
    static template = "dl_event_live_qa.QaAutoRefresh";
    static props = ["*"];

    setup() {
        this.state = useState({
            paused: false,
            refreshing: false,
            lastUpdate: null,
        });
        this.intervalId = null;

        onMounted(() => this._startPolling());
        onWillUnmount(() => this._stopPolling());
    }

    get record() {
        return this.props.record;
    }

    get isActive() {
        return (
            this.record &&
            this.record.data &&
            this.record.data.qa_state === "active"
        );
    }

    _startPolling() {
        if (this.intervalId) {
            return;
        }
        this.intervalId = window.setInterval(
            () => this._tick(),
            POLL_INTERVAL_MS,
        );
    }

    _stopPolling() {
        if (this.intervalId) {
            window.clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    async _tick() {
        if (this.state.paused || this.state.refreshing) {
            return;
        }
        if (!this.isActive) {
            return;
        }
        const record = this.record;
        // Never clobber unsaved edits.
        if (!record || record.dirty || record.isDirty) {
            return;
        }
        this.state.refreshing = true;
        try {
            // Reload the record from the server. Tries record.load() first
            // (Odoo 17/18/19 relational model API), falls back to model.load.
            if (typeof record.load === "function") {
                await record.load();
            } else if (record.model && typeof record.model.load === "function") {
                await record.model.load({ resId: record.resId });
            }
            this.state.lastUpdate = new Date();
        } catch (e) {
            console.warn("QA auto-refresh failed:", e);
        } finally {
            this.state.refreshing = false;
        }
    }

    togglePause() {
        this.state.paused = !this.state.paused;
    }
}

registry.category("view_widgets").add("qa_auto_refresh", {
    component: QaAutoRefresh,
});
