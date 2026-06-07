import re
import unicodedata
from odoo import models, fields, api


class ConfEvent(models.Model):
    _name = 'conf.event'
    _description = 'Conference Event'
    _order = 'date desc, id desc'

    name = fields.Char(string="Nom de l'événement", required=True)
    description = fields.Text(string='Description')
    date = fields.Date(string='Date')
    status = fields.Selection([
        ('draft', 'Planifié'),
        ('live', 'En Live'),
        ('closed', 'Clôturé'),
    ], string='Statut', default='draft', required=True)
    slug = fields.Char(string='Slug URL', readonly=True, copy=False, index=True)
    question_ids = fields.One2many('conf.question', 'event_id', string='Questions')
    question_count = fields.Integer(compute='_compute_counts', string='Total questions', store=True)
    pending_count = fields.Integer(compute='_compute_counts', string='En attente', store=True)
    read_count = fields.Integer(compute='_compute_counts', string='Traitées', store=True)

    _sql_constraints = [
        ('slug_unique', 'UNIQUE(slug)', 'Ce slug est déjà utilisé par un autre événement.'),
    ]

    @api.depends('question_ids', 'question_ids.state')
    def _compute_counts(self):
        for rec in self:
            qs = rec.question_ids
            rec.question_count = len(qs)
            rec.pending_count = len(qs.filtered(lambda q: q.state == 'pending'))
            rec.read_count = len(qs.filtered(lambda q: q.state in ('read', 'skipped')))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if not record.slug:
                record.slug = record._generate_slug()
        return records

    def _generate_slug(self):
        name = self.name or ''
        slug = name.lower()
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')
        slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-') or 'event'
        return f"{slug}-{self.id}"

    def action_set_live(self):
        self.status = 'live'

    def action_set_draft(self):
        self.status = 'draft'

    def action_set_closed(self):
        self.status = 'closed'

    def action_open_dashboard(self):
        return {
            'type': 'ir.actions.act_url',
            'url': f'/conf/dashboard/{self.id}',
            'target': 'new',
        }

    def action_open_public_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return {
            'type': 'ir.actions.act_url',
            'url': f'{base_url}/event/{self.slug}',
            'target': 'new',
        }
