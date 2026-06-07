from odoo import http
from odoo.http import request


class CeoMembershipPortal(http.Controller):

    @http.route(['/adhesion-ceo'], type='http', auth='public', website=True)
    def membership_form(self, **kw):
        plans = request.env['ceo.membership.plan'].sudo().search([('active', '=', True)], order='sequence')
        return request.render('ceo_membership.portal_membership_form', {'plans': plans})

    @http.route(['/adhesion-ceo/submit'], type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def membership_submit(self, **post):
        vals = {
            'company_name': post.get('company_name'),
            'commercial_name': post.get('commercial_name'),
            'member_profile': post.get('member_profile'),
            'plan_id': int(post.get('plan_id')) if post.get('plan_id') else False,
            'contact_name': post.get('contact_name'),
            'contact_function': post.get('contact_function'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'whatsapp': post.get('whatsapp'),
            'wilaya': post.get('wilaya'),
            'commune': post.get('commune'),
            'sector': post.get('sector'),
            'employee_range': post.get('employee_range'),
            'digital_maturity': post.get('digital_maturity'),
            'opex_maturity': post.get('opex_maturity'),
            'motivation': post.get('motivation'),
            'pain_points': post.get('pain_points'),
            'interest_opex': bool(post.get('interest_opex')),
            'interest_ai': bool(post.get('interest_ai')),
            'interest_digital': bool(post.get('interest_digital')),
            'interest_maintenance': bool(post.get('interest_maintenance')),
            'interest_quality': bool(post.get('interest_quality')),
            'interest_training': bool(post.get('interest_training')),
            'wants_project': bool(post.get('wants_project')),
            'wants_support': bool(post.get('wants_support')),
            'wants_sponsor': bool(post.get('wants_sponsor')),
            'state': 'submitted',
        }
        app = request.env['ceo.membership.application'].sudo().create(vals)
        return request.render('ceo_membership.portal_membership_thanks', {'application': app})
