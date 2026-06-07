from odoo import http
from odoo.http import request


class CeoRoadshowController(http.Controller):

    @http.route('/ceo-roadshow-sba', type='http', auth='public', website=True, sitemap=True)
    def ceo_roadshow_sba(self, **kwargs):
        """Public landing page for the CEO Roadshow 2026 event at Sidi Bel Abbès."""
        return request.render('ceo_roadshow_landing.ceo_roadshow_page', {})

    @http.route('/matinee-excellence', type='http', auth='public', website=True, sitemap=True)
    def matinee_excellence(self, **kwargs):
        """Public landing page for the Matinée de l'Excellence Opérationnelle event."""
        return request.render('ceo_roadshow_landing.matinee_excellence_page', {})
