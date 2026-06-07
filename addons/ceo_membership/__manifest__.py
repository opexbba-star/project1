{
    'name': 'CEO Cluster Membership',
    'version': '19.0.1.0.0',
    'summary': 'Gestion des adhésions au Cluster CEO / OPEX',
    'description': """
CEO Cluster Membership
======================
Module MVP pour gérer les demandes d'adhésion, les formules, le workflow de validation,
les membres, le portail adhérent et la préparation à la facturation.
    """,
    'author': 'DELTALOG / CEO Cluster',
    'website': 'https://ceo.deltalog.dz',
    'category': 'Association/CRM',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts', 'crm', 'website', 'portal', 'sale_management', 'account'],
    'data': [
        'security/ceo_membership_security.xml',
        'security/ir.model.access.csv',
        'data/ceo_membership_plan_data.xml',
        'views/ceo_membership_plan_views.xml',
        'views/ceo_membership_application_views.xml',
        'views/ceo_membership_member_views.xml',
        'views/ceo_membership_menus.xml',
        'views/portal_templates.xml',
    ],
    'application': True,
    'installable': True,
}
