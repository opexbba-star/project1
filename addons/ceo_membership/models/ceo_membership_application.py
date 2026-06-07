from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CeoMembershipApplication(models.Model):
    _name = 'ceo.membership.application'
    _description = 'Demande d’adhésion CEO'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(default=lambda self: _('Nouvelle demande'), copy=False, readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('submitted', 'Soumise'),
        ('review', 'En vérification'),
        ('need_more_info', 'Complément demandé'),
        ('committee', 'En validation comité'),
        ('accepted', 'Acceptée'),
        ('waiting_payment', 'En attente paiement'),
        ('active', 'Active'),
        ('refused', 'Refusée'),
        ('cancelled', 'Annulée'),
    ], default='draft', tracking=True)

    partner_id = fields.Many2one('res.partner', string='Organisation / Contact', tracking=True)
    company_name = fields.Char(required=True, tracking=True)
    commercial_name = fields.Char()
    legal_status = fields.Selection([
        ('person', 'Personne physique'),
        ('eurl', 'EURL'),
        ('sarl', 'SARL'),
        ('spa', 'SPA'),
        ('association', 'Association'),
        ('institution', 'Institution'),
        ('other', 'Autre'),
    ], string='Statut juridique')
    rc_number = fields.Char(string='RC')
    nif = fields.Char(string='NIF')
    nis = fields.Char(string='NIS')
    creation_year = fields.Integer(string='Année de création')
    wilaya = fields.Char()
    commune = fields.Char()
    address = fields.Text()
    website = fields.Char()
    social_url = fields.Char(string='LinkedIn / Facebook')

    contact_name = fields.Char(required=True)
    contact_function = fields.Char()
    email = fields.Char(required=True)
    phone = fields.Char(required=True)
    whatsapp = fields.Char()
    preferred_language = fields.Selection([('fr', 'Français'), ('ar', 'Arabe'), ('en', 'Anglais')], default='fr')

    member_profile = fields.Selection([
        ('micro', 'Micro-Entreprise'),
        ('startup', 'Startup'),
        ('pme', 'PME / PMI'),
        ('grand_account', 'Grand Compte'),
        ('expert', 'Expert / Consultant'),
        ('institution', 'Institution / Université'),
        ('sponsor', 'Partenaire Sponsor'),
    ], required=True, tracking=True)
    plan_id = fields.Many2one('ceo.membership.plan', required=True, tracking=True)
    sector = fields.Char(string='Secteur d’activité')
    employee_range = fields.Selection([
        ('1_5', '1 à 5'), ('6_20', '6 à 20'), ('21_50', '21 à 50'),
        ('51_250', '51 à 250'), ('250_plus', '250+')
    ])
    market_scope = fields.Selection([('local', 'Local'), ('national', 'National'), ('export', 'Export')])
    digital_maturity = fields.Selection([('low', 'Faible'), ('medium', 'Moyenne'), ('advanced', 'Avancée')])
    opex_maturity = fields.Selection([('beginner', 'Débutant'), ('intermediate', 'Intermédiaire'), ('advanced', 'Avancé')])
    certifications = fields.Char()
    current_systems = fields.Char(string='SI utilisé')

    motivation = fields.Text()
    pain_points = fields.Text(string='Problèmes prioritaires')
    interest_opex = fields.Boolean('OPEX')
    interest_ai = fields.Boolean('IA')
    interest_digital = fields.Boolean('Digitalisation')
    interest_maintenance = fields.Boolean('Maintenance')
    interest_quality = fields.Boolean('Qualité')
    interest_training = fields.Boolean('Formation')
    wants_project = fields.Boolean('Souhaite proposer un projet')
    wants_support = fields.Boolean('Souhaite être accompagné')
    wants_sponsor = fields.Boolean('Souhaite devenir sponsor')

    score = fields.Integer(compute='_compute_score', store=True)
    expected_fee = fields.Monetary(related='plan_id.annual_fee', currency_field='currency_id')
    currency_id = fields.Many2one(related='plan_id.currency_id')
    sale_order_id = fields.Many2one('sale.order', readonly=True)
    member_id = fields.Many2one('ceo.membership.member', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle demande')) == _('Nouvelle demande'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ceo.membership.application') or _('Nouvelle demande')
        return super().create(vals_list)

    @api.depends('digital_maturity', 'opex_maturity', 'wants_project', 'wants_support', 'wants_sponsor', 'interest_ai', 'interest_opex')
    def _compute_score(self):
        for rec in self:
            score = 0
            score += {'low': 5, 'medium': 10, 'advanced': 15}.get(rec.digital_maturity, 0)
            score += {'beginner': 5, 'intermediate': 10, 'advanced': 15}.get(rec.opex_maturity, 0)
            score += 15 if rec.wants_project else 0
            score += 10 if rec.wants_support else 0
            score += 10 if rec.wants_sponsor else 0
            score += 10 if rec.interest_ai else 0
            score += 10 if rec.interest_opex else 0
            rec.score = score

    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_review(self):
        self.write({'state': 'review'})

    def action_need_more_info(self):
        self.write({'state': 'need_more_info'})

    def action_committee(self):
        self.write({'state': 'committee'})

    def action_accept(self):
        self.write({'state': 'accepted'})

    def action_refuse(self):
        self.write({'state': 'refused'})

    def action_waiting_payment(self):
        self.write({'state': 'waiting_payment'})

    def action_create_partner(self):
        for rec in self:
            if rec.partner_id:
                continue
            partner = self.env['res.partner'].create({
                'name': rec.company_name,
                'company_type': 'company',
                'email': rec.email,
                'phone': rec.phone,
                'website': rec.website,
                'street': rec.address,
                'city': rec.commune,
            })
            self.env['res.partner'].create({
                'name': rec.contact_name,
                'parent_id': partner.id,
                'type': 'contact',
                'function': rec.contact_function,
                'email': rec.email,
                'phone': rec.phone,
            })
            rec.partner_id = partner.id

    def action_activate_membership(self):
        for rec in self:
            rec.action_create_partner()
            start = fields.Date.context_today(rec)
            end = start + relativedelta(months=rec.plan_id.duration_months)
            member = self.env['ceo.membership.member'].create({
                'partner_id': rec.partner_id.id,
                'application_id': rec.id,
                'plan_id': rec.plan_id.id,
                'start_date': start,
                'end_date': end,
                'state': 'active',
            })
            rec.write({'state': 'active', 'member_id': member.id})

    def action_create_sale_order(self):
        product = self.env.ref('ceo_membership.product_ceo_membership_fee', raise_if_not_found=False)
        for rec in self:
            rec.action_create_partner()
            if not product:
                raise UserError(_('Produit de cotisation introuvable.'))
            order = self.env['sale.order'].create({
                'partner_id': rec.partner_id.id,
                'origin': rec.name,
                'order_line': [(0, 0, {
                    'product_id': product.id,
                    'name': 'Cotisation CEO - %s' % rec.plan_id.name,
                    'product_uom_qty': 1,
                    'price_unit': rec.plan_id.annual_fee,
                })]
            })
            rec.write({'sale_order_id': order.id, 'state': 'waiting_payment'})
