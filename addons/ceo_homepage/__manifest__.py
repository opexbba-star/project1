{
    'name': 'CEO Homepage',
    'version': '19.0.1.0.0',
    'summary': 'Custom homepage for ceo.deltalog.dz — OPEX.IA 2030',
    'author': 'Deltalog',
    'category': 'Website',
    'depends': ['website', 'website_event'],
    'data': [
        'views/ceo_homepage_template.xml',
        'views/ceo_partners_template.xml',
        'views/ceo_documentation_template.xml',
        'views/ceo_academy_templates.xml',
        'views/website_menu.xml',
        'views/website_event_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ceo_homepage/static/src/css/ceo_homepage.css',
            'ceo_homepage/static/src/js/ceo_homepage.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
