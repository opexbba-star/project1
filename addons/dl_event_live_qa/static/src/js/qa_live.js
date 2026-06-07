/** @odoo-module **/

/*
 * Event Live Q&A — frontend script
 *
 * Loaded on every website page via web.assets_frontend. It self-activates
 * only when a `.o_event_qa_live` container is present, so it has no cost
 * on the rest of the website.
 *
 * - Polls /event/qa/<token>/questions every 10s (JSON-RPC)
 * - Submits new questions via /event/qa/<token>/submit
 * - Sends upvotes via /event/qa/<token>/vote
 * - Tracks "already voted" question IDs in sessionStorage so the same
 *   browser tab can't double-vote (client-side only — see controller).
 */
(function () {
    "use strict";

    const POLL_INTERVAL_MS = 10000;

    function init() {
        const container = document.querySelector(".o_event_qa_live");
        if (!container) {
            return;
        }

        const token = container.dataset.token;
        const isPresenter = container.dataset.presenter === "1";
        const listEl = container.querySelector(".o_qa_questions_list");
        const submitForm = container.querySelector(".o_qa_submit_form");

        const votedKey = "event_qa_voted_" + token;

        function getVoted() {
            try {
                return JSON.parse(sessionStorage.getItem(votedKey) || "[]");
            } catch (e) {
                return [];
            }
        }

        function addVoted(id) {
            const v = getVoted();
            if (!v.includes(id)) {
                v.push(id);
                try {
                    sessionStorage.setItem(votedKey, JSON.stringify(v));
                } catch (e) {
                    // Storage may be disabled — non-fatal.
                }
            }
        }

        // Odoo `type='json'` controllers expect a JSON-RPC envelope.
        async function rpc(url, params) {
            const response = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    jsonrpc: "2.0",
                    method: "call",
                    params: params || {},
                }),
            });
            if (!response.ok) {
                throw new Error("HTTP " + response.status);
            }
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error.message || "RPC error");
            }
            return data.result;
        }

        function escapeHtml(s) {
            const div = document.createElement("div");
            div.textContent = s == null ? "" : String(s);
            return div.innerHTML;
        }

        function renderQuestions(questions) {
            if (!listEl) {
                return;
            }
            const voted = getVoted();

            if (!questions || questions.length === 0) {
                listEl.innerHTML =
                    '<div class="o_qa_empty">' +
                        '<p>Aucune question pour le moment. <strong>Soyez le premier à demander !</strong></p>' +
                    "</div>";
                return;
            }

            const html = questions.map(function (q) {
                const hasVoted = voted.includes(q.id);
                const answered = q.state === "answered";
                const disabled = hasVoted || isPresenter ? "disabled" : "";
                const answeredBadge = answered
                    ? '<span class="badge text-bg-info">Répondue</span>'
                    : "";
                return (
                    '<div class="o_qa_question_card" data-question-id="' + q.id + '">' +
                        '<div class="card-body">' +
                            '<div class="o_qa_vote_section">' +
                                '<button class="o_qa_vote_btn" ' +
                                        'data-question-id="' + q.id + '" ' + disabled + ' ' +
                                        'aria-label="Voter pour cette question">' +
                                    "▲" +
                                "</button>" +
                                '<div class="o_qa_vote_count">' + q.vote_count + "</div>" +
                            "</div>" +
                            '<div class="o_qa_question_body">' +
                                '<p class="o_qa_question_text">' + escapeHtml(q.question_text) + "</p>" +
                                "<small>— " + escapeHtml(q.author_name) + "</small>" +
                                answeredBadge +
                            "</div>" +
                        "</div>" +
                    "</div>"
                );
            }).join("");

            listEl.innerHTML = html;

            if (!isPresenter) {
                listEl.querySelectorAll(".o_qa_vote_btn").forEach(function (btn) {
                    btn.addEventListener("click", onVoteClick);
                });
            }
        }

        async function fetchQuestions() {
            try {
                const result = await rpc("/event/qa/" + token + "/questions", {});
                if (result && Array.isArray(result.questions)) {
                    renderQuestions(result.questions);
                }
            } catch (e) {
                // Network blips are expected during a long-running session.
                console.warn("Q&A: failed to fetch questions", e);
            }
        }

        async function onVoteClick(e) {
            const btn = e.currentTarget;
            const qid = parseInt(btn.dataset.questionId, 10);
            if (!qid) {
                return;
            }
            const voted = getVoted();
            if (voted.includes(qid)) {
                return;
            }
            btn.disabled = true;
            try {
                const result = await rpc("/event/qa/" + token + "/vote", {
                    question_id: qid,
                });
                if (result && result.success) {
                    addVoted(qid);
                    await fetchQuestions();
                } else {
                    btn.disabled = false;
                }
            } catch (err) {
                btn.disabled = false;
                console.warn("Q&A: vote failed", err);
            }
        }

        async function onSubmit(e) {
            e.preventDefault();
            const textInput = submitForm.querySelector(".o_qa_question_input");
            const authorInput = submitForm.querySelector(".o_qa_author_input");
            const feedback = submitForm.querySelector(".o_qa_submit_feedback");

            const text = (textInput.value || "").trim();
            const author = (authorInput.value || "").trim();

            if (!text) {
                feedback.textContent = "Veuillez saisir une question.";
                feedback.className = "o_qa_submit_feedback ms-3 small text-danger";
                return;
            }

            // Mapping des codes d'erreur du contrôleur vers des messages FR.
            const errorMessages = {
                track_not_found: "Session introuvable.",
                qa_not_active: "Ce Q&A n'est plus actif.",
                empty_question: "Veuillez saisir une question.",
                session_not_found: "Session introuvable.",
                session_not_active: "Cette session n'est plus active.",
                question_not_found: "Question introuvable.",
                question_not_visible: "Cette question n'est plus visible.",
                invalid_question_id: "Identifiant de question invalide.",
            };

            try {
                const result = await rpc("/event/qa/" + token + "/submit", {
                    question_text: text,
                    author_name: author,
                });
                if (result && result.success) {
                    textInput.value = "";
                    feedback.textContent = "Merci ! Votre question est en attente de modération.";
                    feedback.className = "o_qa_submit_feedback ms-3 small text-success";
                } else {
                    const code = result && result.error;
                    feedback.textContent =
                        errorMessages[code] || "Échec de l'envoi. Veuillez réessayer.";
                    feedback.className = "o_qa_submit_feedback ms-3 small text-danger";
                }
            } catch (err) {
                feedback.textContent = "Erreur réseau. Veuillez réessayer.";
                feedback.className = "o_qa_submit_feedback ms-3 small text-danger";
            }
        }

        if (submitForm) {
            submitForm.addEventListener("submit", onSubmit);
        }

        fetchQuestions();
        setInterval(fetchQuestions, POLL_INTERVAL_MS);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
