import logging

from odoo import fields, http
from odoo.http import request

_logger = logging.getLogger(__name__)

# Hard limits to protect the public endpoints from abuse
MAX_QUESTION_LEN = 1000
MAX_AUTHOR_LEN = 100


class EventQAController(http.Controller):
    """Public website endpoints for live Q&A on event.track.

    The `qa_access_token` of a track is the only secret — anyone with the
    link can read approved questions, submit a question, or upvote.
    Public users have no ORM-level rights on `event.qa.question`, so all
    writes go through `sudo()` with the token acting as authorization.
    """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_track(self, token):
        if not token:
            return False
        return request.env['event.track'].sudo().search(
            [('qa_access_token', '=', token), ('qa_enabled', '=', True)],
            limit=1)

    def _serialize_questions(self, track, only_approved=True):
        questions = track.qa_question_ids
        if only_approved:
            questions = questions.filtered(
                lambda q: q.state in ('approved', 'answered'))
        # Sort: votes desc, then oldest first (stable ordering on the page)
        questions = questions.sorted(
            key=lambda q: (-q.vote_count, q.create_date or fields.Datetime.now()))
        return [{
            'id': q.id,
            'author_name': q.author_name or 'Anonymous',
            'question_text': q.question_text,
            'vote_count': q.vote_count,
            'state': q.state,
            'create_date': q.create_date.isoformat() if q.create_date else None,
        } for q in questions]

    # ------------------------------------------------------------------
    # HTML pages
    # ------------------------------------------------------------------
    @http.route(
        ['/event/qa/<string:token>'],
        type='http', auth='public', website=True, sitemap=False,
    )
    def qa_public_page(self, token, **kw):
        """Public Q&A page — participants submit and vote here."""
        track = self._get_track(token)
        if not track:
            return request.not_found()
        return request.render('dl_event_live_qa.qa_public_page', {
            'track': track,
        })

    @http.route(
        ['/event/qa/<string:token>/presenter'],
        type='http', auth='public', website=True, sitemap=False,
    )
    def qa_presenter_view(self, token, **kw):
        """Full-screen view for projection during the event."""
        track = self._get_track(token)
        if not track:
            return request.not_found()
        return request.render('dl_event_live_qa.qa_presenter_view', {
            'track': track,
        })

    # ------------------------------------------------------------------
    # JSON-RPC endpoints (called via fetch from the public page)
    # ------------------------------------------------------------------
    @http.route(
        ['/event/qa/<string:token>/questions'],
        type='json', auth='public', methods=['POST'], csrf=False,
    )
    def qa_questions(self, token, **kw):
        """Returns the list of visible questions sorted by votes desc."""
        track = self._get_track(token)
        if not track:
            return {'error': 'track_not_found'}
        return {
            'qa_state': track.qa_state,
            'track_name': track.name,
            'questions': self._serialize_questions(track, only_approved=True),
        }

    @http.route(
        ['/event/qa/<string:token>/submit'],
        type='json', auth='public', methods=['POST'], csrf=False,
    )
    def qa_submit(self, token, question_text=None, author_name=None, **kw):
        """Public submission endpoint. New questions land in `pending`."""
        track = self._get_track(token)
        if not track:
            return {'error': 'track_not_found'}
        if track.qa_state != 'active':
            return {'error': 'qa_not_active'}

        text = (question_text or '').strip()
        if not text:
            return {'error': 'empty_question'}
        if len(text) > MAX_QUESTION_LEN:
            text = text[:MAX_QUESTION_LEN]

        author = (author_name or '').strip() or 'Anonymous'
        if len(author) > MAX_AUTHOR_LEN:
            author = author[:MAX_AUTHOR_LEN]

        question = request.env['event.qa.question'].sudo().create({
            'track_id': track.id,
            'author_name': author,
            'question_text': text,
            'state': 'pending',
        })
        return {'success': True, 'question_id': question.id}

    @http.route(
        ['/event/qa/<string:token>/vote'],
        type='json', auth='public', methods=['POST'], csrf=False,
    )
    def qa_vote(self, token, question_id=None, **kw):
        """Increments the vote counter for an approved question.

        Per-user deduplication is enforced client-side (sessionStorage);
        this endpoint is intentionally idempotency-free to stay simple.
        For stricter dedup, persist (question_id, ip_or_visitor_id) pairs.
        """
        track = self._get_track(token)
        if not track:
            return {'error': 'track_not_found'}
        try:
            qid = int(question_id)
        except (TypeError, ValueError):
            return {'error': 'invalid_question_id'}

        question = request.env['event.qa.question'].sudo().browse(qid)
        if not question.exists() or question.track_id.id != track.id:
            return {'error': 'question_not_found'}
        if question.state not in ('approved', 'answered'):
            return {'error': 'question_not_visible'}

        question.vote_count = question.vote_count + 1
        return {'success': True, 'vote_count': question.vote_count}
