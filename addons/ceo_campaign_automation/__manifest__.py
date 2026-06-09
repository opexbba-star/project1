{
    'name': 'CEO AI Campaign Automation',
    'version': '19.0.1.0.0',
    'summary': 'Automatisation de campagnes marketing propulsée par l\'IA (Gemini Flash)',
    'description': """
CEO AI Campaign Automation
==========================
Ce module gère l'automatisation de campagnes marketing intelligentes :
- Définition du thème, titre, description et critères de ciblage (région, domaine d'activité).
- Extraction d'un échantillon de contacts directement depuis la base de données locale (res.partner).
- Génération personnalisée du corps des e-mails via l'IA Google Gemini 1.5 Flash.
- Édition manuelle et reformulation assistée par l'IA avant envoi.
- Importation intelligente et automatique Excel/CSV de contacts avec mapping heuristique et IA.
    """,
    'author': 'DELTALOG / CEO Cluster',
    'website': 'https://ceo.deltalog.dz',
    'category': 'Marketing/Email Marketing',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/campaign_import_wizard_views.xml',
        'views/contact_template_wizard_views.xml',
        'views/campaign_automation_views.xml',
        'views/res_config_settings_views.xml',
        'views/campaign_menus.xml',
    ],
    'application': True,
    'installable': True,
}
