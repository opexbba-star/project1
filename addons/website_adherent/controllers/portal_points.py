from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class PortalPoints(CustomerPortal):

    @http.route(['/my/points'], type='http', auth="user", website=True)
    def portal_my_points(self, **kwargs):
        user = request.env.user

        values = {
            'page_name': 'my_points',
            'points': user.x_points,
            'requested_points': user.x_requested_points,
        }
        return request.render("website_adherent.portal_my_points", values)

    @http.route(['/my/points/request'], type='http', auth="user", website=True, csrf=True, methods=['POST'])
    def request_points(self, **kwargs):
        user = request.env.user
        if not user.x_is_adherent:
            return request.redirect('/my')

        val = int(kwargs.get("request_points", 0))
        if val > 0:
            # Update points requested
            user.sudo().write({
                'x_requested_points': user.x_requested_points + val
            })

            # Prepare email body HTML
            notification_body = f"""
                <p>Bonjour,</p>
                <p>L'utilisateur a demandé un ajout de points via le site :</p>
                <ul>
                    <li><strong>Utilisateur :</strong> {user.name}</li>
                    <li><strong>Email :</strong> {user.email}</li>
                    <li><strong>Points demandés :</strong> {val}</li>
                    <li><strong>Total points demandés maintenant :</strong> {user.x_requested_points}</li>
                    <li><strong>Voir l'utilisateur :</strong>
                        <a href="/odoo/users/{user.id}">Ouvrir dans Odoo</a>
                    </li>
                </ul>
                <p>Merci de valider ou refuser cette demande.</p>
            """

            notification_values = {
                'subject': f"Demande de points: {user.name}",
                'body_html': notification_body,
                'email_to': 'maroua.sedoud@inkidia.dz',  # 👈 Change to your admin email
                'email_from': user.company_id.email or 'noreply@example.com',
                'model': 'res.users',
                'res_id': user.id,
            }

            try:
                mail = request.env['mail.mail'].sudo().create(notification_values)
                mail.send()
            except Exception:
                pass  # Do not crash user flow if email fails

        return request.redirect('/my/points')
