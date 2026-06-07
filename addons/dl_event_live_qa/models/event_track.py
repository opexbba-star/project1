import uuid
from urllib.parse import quote

from odoo import api, fields, models


class EventTrack(models.Model):
    """Ajoute les champs Live Q&A directement sur event.track.

    Chaque session de conférence (event.track) peut héberger son propre Q&A :
    l'activer, partager l'URL publique, projeter la vue présentateur.
    """
    _inherit = 'event.track'

    qa_enabled = fields.Boolean(
        string='Q&A en direct',
        default=False,
        copy=False,
    )
    qa_state = fields.Selection(
        selection=[
            ('draft', 'Brouillon'),
            ('active', 'Actif'),
            ('done', 'Terminé'),
        ],
        string='Statut Q&A',
        default='draft',
        copy=False,
    )
    qa_access_token = fields.Char(
        string='Jeton d\'accès Q&A',
        copy=False,
        readonly=True,
        index=True,
    )
    qa_question_ids = fields.One2many(
        comodel_name='event.qa.question',
        inverse_name='track_id',
        string='Questions Q&A',
    )
    qa_question_count = fields.Integer(
        compute='_compute_qa_question_counts',
        string='Nb questions',
    )
    qa_pending_count = fields.Integer(
        compute='_compute_qa_question_counts',
        string='En attente',
    )
    qa_approved_count = fields.Integer(
        compute='_compute_qa_question_counts',
        string='Approuvées',
    )
    qa_public_url = fields.Char(
        compute='_compute_qa_urls',
        string='Lien public Q&A',
    )
    qa_presenter_url = fields.Char(
        compute='_compute_qa_urls',
        string='Lien présentateur Q&A',
    )
    qa_public_qr_url = fields.Char(
        compute='_compute_qa_urls',
        string='QR code (lien public)',
    )

    # ------------------------------------------------------------------
    # Computes
    # ------------------------------------------------------------------
    @api.depends('qa_question_ids', 'qa_question_ids.state')
    def _compute_qa_question_counts(self):
        for track in self:
            questions = track.qa_question_ids
            track.qa_question_count = len(questions)
            track.qa_approved_count = len(
                questions.filtered(lambda q: q.state == 'approved'))
            track.qa_pending_count = len(
                questions.filtered(lambda q: q.state == 'pending'))

    @api.depends('qa_access_token')
    def _compute_qa_urls(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url', default='')
        for track in self:
            if track.qa_access_token:
                track.qa_public_url = '%s/event/qa/%s' % (
                    base_url, track.qa_access_token)
                track.qa_presenter_url = '%s/event/qa/%s/presenter' % (
                    base_url, track.qa_access_token)
                track.qa_public_qr_url = (
                    '/report/barcode/?barcode_type=QR'
                    '&value=%s&width=220&height=220&humanreadable=0'
                ) % quote(track.qa_public_url, safe='')
            else:
                track.qa_public_url = False
                track.qa_presenter_url = False
                track.qa_public_qr_url = False

    # ------------------------------------------------------------------
    # Gestion du jeton
    # ------------------------------------------------------------------
    def _ensure_qa_token(self):
        for track in self:
            if not track.qa_access_token:
                track.qa_access_token = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Actions Q&A
    # ------------------------------------------------------------------
    def action_qa_activate(self):
        self._ensure_qa_token()
        self.write({'qa_enabled': True, 'qa_state': 'active'})

    def action_qa_close(self):
        self.write({'qa_state': 'done'})

    def action_qa_draft(self):
        self.write({'qa_state': 'draft'})

    def action_qa_regenerate_token(self):
        """Invalide les URLs publique/présentateur en générant un nouveau jeton."""
        for track in self:
            track.qa_access_token = str(uuid.uuid4())
        return True

    def action_qa_view_public(self):
        self.ensure_one()
        self._ensure_qa_token()
        return {
            'type': 'ir.actions.act_url',
            'url': '/event/qa/%s' % self.qa_access_token,
            'target': 'new',
        }

    def action_qa_view_presenter(self):
        self.ensure_one()
        self._ensure_qa_token()
        return {
            'type': 'ir.actions.act_url',
            'url': '/event/qa/%s/presenter' % self.qa_access_token,
            'target': 'new',
        }

    def action_qa_view_questions(self):
        """Ouvre la liste des questions Q&A filtrées sur cette session."""
        self.ensure_one()
        return {
            'name': 'Questions Q&A',
            'type': 'ir.actions.act_window',
            'res_model': 'event.qa.question',
            'view_mode': 'kanban,list,form',
            'domain': [('track_id', '=', self.id)],
            'context': {'default_track_id': self.id},
        }
