{
    'name': 'Signup Form Customization',
    'version': '1.0',
    'summary': 'Adds company, position, phone and LinkedIn profile to the signup form.',
    'author': 'Deltalog Odoo Dev Team',
    'category': 'Website',
    'depends': ['auth_signup', 'website'], # Très important: notre module dépend de auth_signup
    'data': [
        'views/auth_signup_templates.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}