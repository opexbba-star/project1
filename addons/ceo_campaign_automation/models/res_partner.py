# -*- coding: utf-8 -*-
from odoo import models, fields

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
