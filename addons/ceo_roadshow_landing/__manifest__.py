{
    'name': 'CEO Roadshow — Landing Page SBA 2026',
    'version': '1.0',
    'summary': 'Landing page for CEO Roadshow 2026 event at Université Djilali Liabes, Sidi Bel Abbès',
    'description': """
        Custom landing page module for the CEO Roadshow 2026 event.
        Adds a dedicated public page at /ceo-roadshow-sba and registers it
        in the website main navigation menu.
    """,
    'category': 'Website',
    'author': 'Deltalog Odoo Dev Team',
    'depends': ['website'],
    'data': [
        'views/ceo_roadshow_template.xml',
        'views/matinee_excellence_template.xml',
        'views/website_menu.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'ceo_roadshow_landing/static/src/css/ceo_roadshow.css',
            'ceo_roadshow_landing/static/src/js/ceo_roadshow.js',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
