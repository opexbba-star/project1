from odoo import http
from odoo.http import request


class ConfQuestionsController(http.Controller):

    # ─── Public event page ───────────────────────────────────────────────────

    @http.route('/event/<string:slug>', type='http', auth='public', csrf=False)
    def event_public(self, slug, **kwargs):
        event = request.env['conf.event'].sudo().search([('slug', '=', slug)], limit=1)
        if not event:
            return request.not_found()
        return request.render('conf_questions.template_event_public', {
            'event': event,
            'success': False,
            'error': None,
            'submitter_name': '',
            'question_text': '',
        })

    @http.route('/event/<string:slug>/submit', type='http', auth='public',
                methods=['POST'], csrf=False)
    def event_submit_question(self, slug, **kwargs):
        event = request.env['conf.event'].sudo().search([('slug', '=', slug)], limit=1)
        if not event:
            return request.not_found()

        submitter_name = (kwargs.get('submitter_name') or '').strip()
        question_text = (kwargs.get('question_text') or '').strip()

        if event.status == 'closed':
            error = 'Cet événement est clôturé. Les questions ne sont plus acceptées.'
        elif not submitter_name:
            error = 'Le prénom est requis.'
        elif not question_text:
            error = 'La question est requise.'
        else:
            error = None

        if error:
            return request.render('conf_questions.template_event_public', {
                'event': event,
                'success': False,
                'error': error,
                'submitter_name': submitter_name,
                'question_text': question_text,
            })

        request.env['conf.question'].sudo().create({
            'event_id': event.id,
            'submitter_name': submitter_name,
            'question_text': question_text,
        })
        return request.render('conf_questions.template_event_public', {
            'event': event,
            'success': True,
            'error': None,
            'submitter_name': '',
            'question_text': '',
        })

    # ─── Admin events overview ────────────────────────────────────────────────

    @http.route('/conf/events', type='http', auth='user')
    def admin_events(self, **kwargs):
        events = request.env['conf.event'].search([], order='date desc')
        ongoing = events.filtered(lambda e: e.status in ('draft', 'live'))
        past = events.filtered(lambda e: e.status == 'closed')
        return request.render('conf_questions.template_admin_events', {
            'events': events,
            'ongoing_events': ongoing,
            'past_events': past,
        })

    @http.route('/conf/events/create', type='http', auth='user', methods=['POST'])
    def admin_create_event(self, **kwargs):
        name = (kwargs.get('event_name') or '').strip()
        description = (kwargs.get('event_description') or '').strip()
        date_str = (kwargs.get('event_date') or '').strip()
        status = kwargs.get('event_status', 'draft')

        if name:
            vals = {
                'name': name,
                'description': description or False,
                'status': status if status in ('draft', 'live') else 'draft',
            }
            if date_str:
                vals['date'] = date_str
            request.env['conf.event'].create(vals)

        return request.redirect('/conf/events')

    # ─── Admin event dashboard ────────────────────────────────────────────────

    @http.route('/conf/dashboard/<int:event_id>', type='http', auth='user')
    def admin_dashboard(self, event_id, **kwargs):
        event = request.env['conf.event'].browse(event_id)
        if not event.exists():
            return request.not_found()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        pending = event.question_ids.filtered(
            lambda q: q.state == 'pending'
        ).sorted('submitted_at')
        history = event.question_ids.filtered(
            lambda q: q.state in ('read', 'skipped')
        ).sorted('submitted_at', reverse=True)
        return request.render('conf_questions.template_admin_dashboard', {
            'event': event,
            'pending_questions': pending,
            'history_questions': history,
            'base_url': base_url,
            'public_url': f'{base_url}/event/{event.slug}',
        })

    @http.route('/conf/dashboard/<int:event_id>/data', type='json', auth='user',
                methods=['POST'], csrf=False)
    def dashboard_data(self, event_id, **kwargs):
        event = request.env['conf.event'].browse(event_id)
        if not event.exists():
            return {'error': 'not found'}

        pending = event.question_ids.filtered(
            lambda q: q.state == 'pending'
        ).sorted('submitted_at')
        history = event.question_ids.filtered(
            lambda q: q.state in ('read', 'skipped')
        ).sorted('submitted_at', reverse=True)

        def fmt(q):
            return {
                'id': q.id,
                'name': q.submitter_name,
                'text': q.question_text,
                'state': q.state,
                'time': q.submitted_at.strftime('%I:%M:%S %p') if q.submitted_at else '',
            }

        return {
            'pending': [fmt(q) for q in pending],
            'history': [fmt(q) for q in history],
            'total': event.question_count,
            'pending_count': event.pending_count,
            'read_count': event.read_count,
            'event_status': event.status,
        }

    # ─── Question actions (AJAX) ──────────────────────────────────────────────

    @http.route('/conf/question/<int:question_id>/read', type='json', auth='user',
                methods=['POST'], csrf=False)
    def question_mark_read(self, question_id, **kwargs):
        q = request.env['conf.question'].browse(question_id)
        if q.exists():
            q.state = 'read'
        return {'ok': True}

    @http.route('/conf/question/<int:question_id>/skip', type='json', auth='user',
                methods=['POST'], csrf=False)
    def question_skip(self, question_id, **kwargs):
        q = request.env['conf.question'].browse(question_id)
        if q.exists():
            q.state = 'skipped'
        return {'ok': True}

    @http.route('/conf/question/<int:question_id>/delete', type='json', auth='user',
                methods=['POST'], csrf=False)
    def question_delete(self, question_id, **kwargs):
        q = request.env['conf.question'].browse(question_id)
        if q.exists():
            q.unlink()
        return {'ok': True}

    # ─── Event status actions (AJAX) ─────────────────────────────────────────

    @http.route('/conf/event/<int:event_id>/close', type='json', auth='user',
                methods=['POST'], csrf=False)
    def event_close(self, event_id, **kwargs):
        event = request.env['conf.event'].browse(event_id)
        if event.exists():
            event.status = 'closed'
        return {'ok': True}

    @http.route('/conf/event/<int:event_id>/live', type='json', auth='user',
                methods=['POST'], csrf=False)
    def event_set_live(self, event_id, **kwargs):
        event = request.env['conf.event'].browse(event_id)
        if event.exists():
            event.status = 'live'
        return {'ok': True}

    @http.route('/conf/event/<int:event_id>/delete', type='json', auth='user',
                methods=['POST'], csrf=False)
    def event_delete(self, event_id, **kwargs):
        event = request.env['conf.event'].browse(event_id)
        if event.exists():
            event.unlink()
        return {'ok': True}
