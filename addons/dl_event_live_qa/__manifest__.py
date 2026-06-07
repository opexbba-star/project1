{
    'name': 'Q&A en Direct (Évènements)',
    'version': '19.0.1.0.0',
    'summary': 'Sessions de Q&A en direct sur les sessions d\'évènement (style Slido)',
    'description': """
Q&A en Direct pour les Évènements
==================================
Ajoute des capacités de Q&A en temps réel directement sur les sessions
d'évènement (event.track) :

* Activer un Q&A en direct sur n'importe quelle session de conférence
* Soumission publique de questions (nominative ou anonyme)
* Vote pour les questions approuvées, tri par nombre de votes
* Modération depuis le backend (approuver / rejeter / marquer comme répondue)
* Page publique en direct avec rafraîchissement automatique toutes les 10s
* Vue Présentateur plein écran pour projection
""",
    'author': 'deltalog',
    'website': 'https://www.deltalog.dz/',
    'category': 'Marketing/Events',
    'license': 'LGPL-3',
    'depends': ['base', 'website_event_track'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/event_qa_question_views.xml',
        'views/event_track_views.xml',
        'views/menu_views.xml',
        'templates/qa_public_page.xml',
        'templates/qa_presenter_view.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'dl_event_live_qa/static/src/css/qa_style.css',
            'dl_event_live_qa/static/src/js/qa_live.js',
        ],
        'web.assets_backend': [
            'dl_event_live_qa/static/src/xml/qa_auto_refresh.xml',
            'dl_event_live_qa/static/src/js/qa_auto_refresh.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
