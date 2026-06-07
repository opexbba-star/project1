{
    'name': 'Website Adhérents',
    'version': '1.0',
    'summary': 'Add Adhérent field to users and control premium access',
    'description': 'This module allows marking users as Adhérents and controlling access to premium content.',
    'category': 'Website',
    'author': 'Deltalog Odoo Dev Team',
    'depends': ['base', 'website_slides', 'website', 'portal', 'auth_signup'],
    'data': [
        'views/res_users_views.xml',
        'views/portal_points.xml',
        'data/mail_template_points.xml',
        'views/slide_channel_views.xml',
        'views/channel_locked.xml',
    ],
    'installable': True,
    'application': False,
}
