from odoo import fields, models


class CeoMembershipMember(models.Model):
    _name = 'ceo.membership.member'
    _description = 'Membre CEO'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'end_date desc'

    partner_id = fields.Many2one('res.partner', required=True, tracking=True)
    application_id = fields.Many2one('ceo.membership.application')
    plan_id = fields.Many2one('ceo.membership.plan', required=True, tracking=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspendue'),
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée'),
    ], default='active', tracking=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    directory_visible = fields.Boolean(default=True)
    representative_name = fields.Char(related='partner_id.name', store=True)
    sector = fields.Char()
    notes = fields.Text()
