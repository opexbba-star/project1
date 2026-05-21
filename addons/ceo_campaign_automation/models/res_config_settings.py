from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Configuration de la base de données Odoo externe (Connecteur XML-RPC)
    external_odoo_url = fields.Char(
        string="URL de l'Odoo Externe",
        config_parameter='ceo_campaign_automation.external_odoo_url',
        help="Exemple : https://mon-odoo-externe.com"
    )
    external_odoo_db = fields.Char(
        string="Nom de la base de données",
        config_parameter='ceo_campaign_automation.external_odoo_db',
        help="Nom de la base de données distante"
    )
    external_odoo_user = fields.Char(
        string="Utilisateur / Email",
        config_parameter='ceo_campaign_automation.external_odoo_user',
        help="Identifiant de connexion à la base distante"
    )
    external_odoo_password = fields.Char(
        string="Mot de passe / Clé API",
        config_parameter='ceo_campaign_automation.external_odoo_password',
        help="Mot de passe ou Clé API (recommandé) pour l'accès XML-RPC"
    )

    # Configuration de l'IA Google Gemini
    gemini_api_key = fields.Char(
        string="Clé API Google Gemini",
        config_parameter='ceo_campaign_automation.gemini_api_key',
        help="Clé API pour Gemini 1.5 Flash (disponible gratuitement sur Google AI Studio)"
    )
