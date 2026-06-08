# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # store=False est crucial ici : cela évite que PostgreSQL ne cherche la colonne en base de données,
    # empêchant l'erreur 500 au login, tout en satisfaisant le validateur de vues au démarrage.
    source_tag = fields.Selection([
        ('excel', 'Import Excel/CSV'),
        ('maps', 'Scraping Google Maps'),
        ('annuaire', 'Scraping Annuaire'),
        ('form', 'Formulaire / Landing Page'),
        ('rs', 'Réseaux Sociaux')
    ], string="Source du contact", store=False)

    email_valid = fields.Boolean(string="Email Valide", default=False, tracking=True)
    phone_valid = fields.Boolean(string="Téléphone Valide", default=False, tracking=True)
    qualification_score = fields.Integer(
        string="Score de Qualification",
        compute="_compute_qualification_score",
        store=True,
        tracking=True
    )

    @api.depends('email_valid', 'phone_valid')
    def _compute_qualification_score(self):
        for record in self:
            score = 0
            if record.email_valid:
                score += 1
            if record.phone_valid:
                score += 1
            record.qualification_score = score
