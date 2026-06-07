{
    'name': "Custom Appointment Booking",
    'version': '1.0',
    'summary': """
        Custom website controller for logged-in users to book appointments directly into the Odoo Calendar.
    """,
    'description': """
        This module provides a custom web page and controller to allow authenticated website users to
        submit an appointment request, which is automatically converted into a calendar event.
    """,
    'author': "Maroua Sedoud",
    'category': 'Website',
    'version': '1.0',
    'depends': [
        'base',
        'web', 
        'website', 
        'calendar', 
        'contacts'
    ],
    'data': [
        # 'views/templates.xml',
        'views/appointment_booking_template.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
