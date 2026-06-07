from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import pytz

class CustomAppointmentBooking(http.Controller):

    @http.route('/my/appointment/book', type='http', auth='user', website=True)
    def appointment_booking_form(self, **kw):
        ICP = request.env['ir.config_parameter'].sudo()
        start_hour = float(ICP.get_param('calendar.allowed_start_hour', 8.0))
        end_hour = float(ICP.get_param('calendar.allowed_end_hour', 17.0))

        # Format hours as "08h00" and "17h00"
        start_str = f"{int(start_hour):02d}h00"
        end_str = f"{int(end_hour):02d}h00"

        user = request.env.user  # ✔ Define user first

        appointments = request.env['calendar.event'].search([
            ('start', '>=', fields.Datetime.now())
        ])

        appointments_display = []

        for appt in appointments:
            start_local = fields.Datetime.context_timestamp(user, appt.start)

            formatted_start = start_local.strftime('%Y-%m-%d %H:%M')

            duration = appt.duration
            hours = int(duration)
            minutes = int((duration % 1) * 60)

            if minutes == 0:
                formatted_duration = f"{hours}h"
            else:
                formatted_duration = (
                    f"{hours}h{minutes:02d}min" if hours > 0 else f"{minutes} min"
                )

            appointments_display.append({
                'start': formatted_start,
                'duration': formatted_duration,
            })

        user_tz = pytz.timezone(user.tz or 'UTC')

        return request.render('custom_appointment_booking.appointment_booking_form_template', {
            'user_name': user.name,
            'user_email': user.email,
            'user_tz': user_tz.zone,
            'appointments_display': appointments_display,
            'start_hour': start_str,
            'end_hour': end_str,
        })

    @http.route('/my/appointment/submit', type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def appointment_booking_submit(self, **post):
        """
        Handles the form submission and creates a calendar event.
        """
        user = request.env.user
        
        # 1.1 Extract and validate form data
        try:
            subject = post.get('appointment_subject')
            start_datetime_str = post.get('appointment_datetime')
            duration_hours = float(post.get('appointment_duration', 0.5)) # Default to 30 minutes
            
            if not subject or not start_datetime_str:
                return request.render('custom_appointment_booking.appointment_booking_error_template', {
                    'error_message': "Missing required fields (Subject or Date/Time).",
                })

            # Convert string datetime to datetime object
            # Assuming the input format from the form is YYYY-MM-DDTHH:MM
            start_dt_naive = datetime.strptime(start_datetime_str, '%Y-%m-%dT%H:%M')
            
            # Localize the naive datetime object to the user's timezone
            user_tz = pytz.timezone(user.tz or 'UTC')
            start_dt_localized = user_tz.localize(start_dt_naive)
            
            # Convert to UTC for Odoo storage
            utc_tz = pytz.timezone('UTC')
            start_dt_utc = start_dt_localized.astimezone(utc_tz)
            
            # Calculate end time
            end_dt_utc = start_dt_utc + timedelta(hours=duration_hours)
            
        except Exception as e:
            return request.render('custom_appointment_booking.appointment_booking_error_template', {
                'error_message': f"Invalid data submission: {e}",
            })
        
        # 1.2 - Check for Overlap
        
        start_dt_str = start_dt_utc.strftime('%Y-%m-%d %H:%M:%S')
        end_dt_str = end_dt_utc.strftime('%Y-%m-%d %H:%M:%S')
        
        overlap_domain = [
            ('stop', '>', start_dt_str),  # Existing event stops after new event starts
            ('start', '<', end_dt_str),   # Existing event starts before new event stops
        ]
        
        existing_overlapping_events = request.env['calendar.event'].sudo().search(overlap_domain)

        if existing_overlapping_events:
            return request.render('custom_appointment_booking.appointment_booking_error_template', {
                'error_message': (
                    "Ce créneau horaire est déjà réservé. Veuillez choisir un autre horaire ou une autre durée."
                ),
            })
        
        # 1.3 - Block Times Outside Working Hours 
        ICP = request.env['ir.config_parameter'].sudo()  # Use sudo() to avoid access issues
        allowed_start_hour = float(ICP.get_param('calendar.allowed_start_hour', default=8.0))
        allowed_end_hour = float(ICP.get_param('calendar.allowed_end_hour', default=17.0))

        # Format hours nicely for the error message
        start_str = f"{int(allowed_start_hour):02d}h00"
        end_str = f"{int(allowed_end_hour):02d}h00"

        # Check starting hour
        if start_dt_localized.hour < allowed_start_hour or start_dt_localized.hour >= allowed_end_hour:
            return request.render('custom_appointment_booking.appointment_booking_error_template', {
                'error_message': f"Les horaires des rendez-vous sont entre {start_str} et {end_str}."
            })


        # 1.4 - Block Fridays
        # Using the localized date so timezone is respected
        local_weekday = start_dt_localized.weekday()  # 0=Mon, ..., 4=Fri

        if local_weekday == 4:
            return request.render('custom_appointment_booking.appointment_booking_error_template', {
                'error_message': "Les rendez-vous ne sont pas disponibles le vendredi."
            })

        # 2. Create the Calendar Event
        try:
            event_vals = {
                'name': subject,
                'start': start_dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'stop': end_dt_utc.strftime('%Y-%m-%d %H:%M:%S'),
                'allday': False,
                'user_id': user.id, # The user who created the event (internal Odoo user)
                'partner_ids': [(4, user.partner_id.id)], # The website user's contact as an attendee
                'description': f"Appointment booked by website user: {user.name} ({user.email})\n"
                               f"Duration: {duration_hours} hours\n"
                               f"Notes: {post.get('appointment_notes', 'N/A')}",
            }
            
            new_event = request.env['calendar.event'].sudo().create(event_vals)

            # 3. Send a confirmation email

            notification_body = f"""
                <p>Bonjour,</p>
                <p>Un nouveau rendez-vous a été réservé via le site web.</p>
                <ul>
                    <li><strong>Sujet:</strong> {subject}</li>
                    <li><strong>Début (UTC):</strong> {start_dt_utc.strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li><strong>Fin (UTC):</strong> {end_dt_utc.strftime('%Y-%m-%d %H:%M:%S')}</li>
                    <li><strong>Durée:</strong> {duration_hours} heures</li>
                </ul>
                <p><strong>Détails du client :</strong></p>
                <ul>
                    <li><strong>Nom:</strong> {user.name}</li>
                    <li><strong>E-mail:</strong> {user.email}</li>
                    <li><strong>Notes:</strong> {post.get('appointment_notes', 'N/A')}</li>
                    <li><strong>Lien vers l'événement:</strong> /web#id={new_event.id}&model=calendar.event&view_type=form</li>
                </ul>
                <p>Veuillez vérifier le calendrier pour plus de détails.</p>
            """
            
            notification_values = {
                'subject': f"NOUVEAU RENDEZ-VOUS RÉSERVÉ: {subject}",
                'body_html': notification_body,
                'email_to': 'maroua.sedoud@inkidia.dz',
                'email_from': request.env.user.company_id.email or 'noreply@example.com',
                'model': 'calendar.event',
                'res_id': new_event.id,
            }
            
            try:
                notification_id = request.env['mail.mail'].sudo().create(notification_values)
                notification_id.send()
            except Exception as notif_e:
                # Log the email error but don't block the transaction
                # print(f"Erreur lors de l'envoi de la notification à l'équipe: {notif_e}")
                pass
        
        except Exception as e:
            # Log the error and inform the user
            request.env.cr.rollback()
            return request.render('custom_appointment_booking.appointment_booking_error_template', {
                'error_message': f"Une erreur s'est produite lors de la réservation. Veuillez réessayer ou contacter l'assistance.",
            })
        
        # 4. Success message
        return request.render('custom_appointment_booking.appointment_booking_success_template', {})
