from odoo import api, fields, models


class CeoMembershipPlan(models.Model):
    _name = 'ceo.membership.plan'
    _description = 'Formule d’adhésion CEO'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    target_profile = fields.Selection([
        ('micro', 'Micro-Entreprise'),
        ('startup', 'Startup'),
        ('pme', 'PME / PMI'),
        ('grand_account', 'Grand Compte'),
        ('expert', 'Expert / Consultant'),
        ('institution', 'Institution / Université'),
        ('sponsor', 'Partenaire Sponsor'),
    ], string='Cible principale')
    duration_months = fields.Integer(default=12, required=True)
    annual_fee = fields.Monetary(string='Cotisation annuelle')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    description = fields.Text()
    benefits = fields.Text(string='Avantages')
    allow_portal_access = fields.Boolean(default=True)
    include_directory_visibility = fields.Boolean(string='Visible dans annuaire')
    include_diagnostic = fields.Boolean(string='Diagnostic flash inclus')
    include_logo_visibility = fields.Boolean(string='Logo visible portail')
    include_copil = fields.Boolean(string='Participation COPIL')
