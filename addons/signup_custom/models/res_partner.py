# signup_customization/controllers/main.py

from odoo import http
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_linkedin_profile = fields.Char(string="Profil LinkedIn")

class AuthSignupHomeInherit(AuthSignupHome ):

    # ON MODIFIE CETTE MÉTHODE
    def get_auth_signup_qcontext(self):
        # On récupère le contexte original
        qcontext = super(AuthSignupHomeInherit, self).get_auth_signup_qcontext()

        # --- NOUVELLE PARTIE : Récupérer les entreprises ---
        # On cherche tous les partenaires qui sont des entreprises (is_company=True)
        # et on les trie par nom pour un affichage propre.
        companies = request.env['res.partner'].sudo().search([
            ('is_company', '=', True)
        ], order='name')
        
        # On ajoute la liste des entreprises au contexte
        qcontext['companies'] = companies
        # --- FIN DE LA NOUVELLE PARTIE ---

        # On garde la logique pour pré-remplir les champs en cas d'erreur
        qcontext.update({
            'company_name': request.params.get('company_name'),
            'position': request.params.get('position'),
            'phone': request.params.get('phone'),
            'x_linkedin_profile': request.params.get('x_linkedin_profile'),
        })
        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = super(AuthSignupHomeInherit, self)._prepare_signup_values(qcontext)

        # --- Logique pour l'entreprise (légèrement modifiée) ---
        company_name = qcontext.get('company_name')
        parent_id = False
        if company_name:
            # On cherche une entreprise qui a exactement ce nom
            company = request.env['res.partner'].sudo().search([
                ('is_company', '=', True),
                ('name', '=', company_name)
            ], limit=1)
            
            if company:
                parent_id = company.id
            else:
                # Si elle n'existe pas, on la crée
                new_company = request.env['res.partner'].sudo().create({
                    'is_company': True,
                    'name': company_name,
                })
                parent_id = new_company.id
        
        values.update({
            'parent_id': parent_id,
            'function': qcontext.get('position'),
            'phone': qcontext.get('phone'),
            'x_linkedin_profile': qcontext.get('x_linkedin_profile'),
        })
        
        return values
