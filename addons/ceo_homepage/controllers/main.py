# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CeoPartners(http.Controller):
    @http.route('/partenaires-sponsors', type='http', auth="public", website=True)
    def partners_page(self, **kwargs):
        partners_data = {
            'government': [
                {'src': '/ceo_homepage/static/src/img/Picture3.png', 'name': 'وزارة التعليم العالي والبحث العلمي'},
                {'src': '/ceo_homepage/static/src/img/Picture2.png', 'name': 'وزارة الصناعة'},
                {'src': '/ceo_homepage/static/src/img/Picture1.png', 'name': 'Ministère de l\'Économie de la connaissance'}
            ],
            'institutions': [
                {'src': '/ceo_homepage/static/src/img/bastp_logo.PNG', 'name': 'Bourse Algérienne de Sous-Traitance'},
                {'src': '/ceo_homepage/static/src/img/Capturekkkk.PNG', 'name': 'CATI - UDL SBA'},
                {'src': '/ceo_homepage/static/src/img/Picture6.jpg', 'name': 'CDE'}
            ],
            'companies': [
                {'src': '/ceo_homepage/static/src/img/Picture8.png', 'name': 'Deltalog'},
                {'src': '/ceo_homepage/static/src/img/uveds_logo.PNG', 'name': 'Uveds'},
                {'src': '/ceo_homepage/static/src/img/miniros_logo.PNG', 'name': 'Miniros'},
                {'src': '/ceo_homepage/static/src/img/Picture4.jpg', 'name': 'Bleu'},
                {'src': '/ceo_homepage/static/src/img/Picture5.jpg', 'name': 'Start\'Dz'},
                {'src': '/ceo_homepage/static/src/img/Picture7.jpg', 'name': 'دار ذكاء اصطناعي'},
                {'src': '/ceo_homepage/static/src/img/Picture9.png', 'name': 'Inkidia'},
                {'src': '/ceo_homepage/static/src/img/Picture10.png', 'name': 'GSH'},
                {'src': '/ceo_homepage/static/src/img/Picture11.jpg', 'name': 'FALMI'}
            ]
        }
        return request.render('ceo_homepage.ceo_partners_page', partners_data)


class CeoDocumentation(http.Controller):
    @http.route('/documentation-opex', type='http', auth="public", website=True)
    def documentation_page(self, **kwargs):
        return request.render('ceo_homepage.ceo_documentation_page', {})


class CeoAcademy(http.Controller):
    @http.route('/opex-academy', type='http', auth="public", website=True)
    def academy_page(self, **kwargs):
        return request.render('ceo_homepage.ceo_academy_page', {})

    @http.route('/opex-academy/atelier-solutions-innovantes', type='http', auth="public", website=True)
    def masterclass_1(self, **kwargs):
        return request.render('ceo_homepage.ceo_masterclass_1', {})

    @http.route('/opex-academy/atelier-qualification-opex', type='http', auth="public", website=True)
    def masterclass_2(self, **kwargs):
        return request.render('ceo_homepage.ceo_masterclass_2', {})

