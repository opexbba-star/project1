from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # Configuration de l'IA Google Gemini
    gemini_api_key = fields.Char(
        string="Clé API Google Gemini",
        config_parameter='ceo_campaign_automation.gemini_api_key',
        help="Clé API pour Gemini 1.5 Flash (disponible gratuitement sur Google AI Studio)"
    )
