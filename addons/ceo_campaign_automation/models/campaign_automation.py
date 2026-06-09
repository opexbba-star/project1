import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CampaignContactLine(models.Model):
    _name = 'campaign.contact.line'
    _description = 'Ligne de Contact Échantillon'

    campaign_id = fields.Many2one('campaign.automation', string="Campagne", ondelete='cascade')
    external_contact_id = fields.Integer(string="ID Externe")
    partner_name = fields.Char(string="Nom du contact", required=True)
    email = fields.Char(string="Email", required=True)
    region = fields.Char(string="Région")
    activity_domain = fields.Char(string="Domaine d'activité")
    preferences = fields.Text(string="Notes / Préférences")

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Envoyé')
    ], string="Statut", default='draft')


class CampaignAutomation(models.Model):
    _name = 'campaign.automation'
    _description = 'Automatisation de Campagne Marketing IA'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Titre de la campagne", required=True, tracking=True)
    theme = fields.Char(string="Thème de la campagne", required=True, tracking=True, help="Ex: Lancement de produit, Invitation Webinaire, etc.")
    description = fields.Text(string="Description & Objectifs", tracking=True, help="Détaillez le message principal et l'appel à l'action (CTA).")
    
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('contacts_fetched', 'Échantillon Sélectionné'),
        ('ai_generated', 'Email Généré'),
        ('ready', 'Prêt à envoyer'),
        ('done', 'Campagne Envoyée')
    ], string="Statut", default='draft', tracking=True)

    # Critères de ciblage (Ciblage & Échantillonnage)
    target_region = fields.Char(string="Région ciblée", help="Ex: Alger, Oran, Paris, etc.")
    target_activity_domain = fields.Char(string="Domaine d'activité", help="Ex: Informatique, Industrie, Santé, etc.")
    sample_limit = fields.Integer(string="Taille de l'échantillon", default=25, help="Nombre maximum de contacts à extraire pour cet échantillon (ex: 25).")
    
    contact_line_ids = fields.One2many('campaign.contact.line', 'campaign_id', string="Contacts de l'échantillon")

    # Contenu unique de l'email pour tout l'échantillon
    generated_subject = fields.Char(string="Objet de l'email", tracking=True)
    generated_body = fields.Html(string="Corps de l'email (IA)", tracking=True)
    rephrase_prompt = fields.Char(string="Instruction de reformulation IA", help="Ex: Rends le texte plus formel, raccourcis le texte, ajoute un PS, etc.")

    # Variables de connexion et d'API saisies directement dans l'interface par l'utilisateur
    gemini_api_key = fields.Char(string="Clé API Google Gemini", default=lambda self: self.env['ir.config_parameter'].sudo().get_param('ceo_campaign_automation.gemini_api_key', ''))

    def _save_connection_params(self):
        """Sauvegarde automatique des paramètres saisis pour les réutiliser dans les futures campagnes."""
        set_param = self.env['ir.config_parameter'].sudo().set_param
        if self.gemini_api_key:
            set_param('ceo_campaign_automation.gemini_api_key', self.gemini_api_key)

    def action_fetch_sample_contacts(self):
        """
        Recherche des contacts dans la base de données locale (res.partner) selon les critères de ciblage.
        """
        self.ensure_one()
        self._save_connection_params()

        try:
            domain = []
            if self.target_region:
                domain.append(('city', 'ilike', self.target_region))
            if self.target_activity_domain:
                domain.append(('function', 'ilike', self.target_activity_domain))

            contacts = self.env['res.partner'].search(domain, limit=self.sample_limit)

            self.contact_line_ids.unlink()

            lines_data = []
            for c in contacts:
                if not c.email:
                    continue
                lines_data.append((0, 0, {
                    'external_contact_id': c.id,
                    'partner_name': c.name,
                    'email': c.email,
                    'region': c.city or self.target_region or '',
                    'activity_domain': c.function or self.target_activity_domain or '',
                    'preferences': c.comment or 'Aucune note spécifique.',
                    'state': 'draft'
                }))

            if not lines_data:
                raise UserError(_("Aucun contact trouvé avec ces critères dans la base de données locale."))

            self.write({
                'contact_line_ids': lines_data,
                'state': 'contacts_fetched'
            })

        except Exception as e:
            raise UserError(_("Erreur lors de la recherche locale : %s") % str(e))

    def action_generate_ai_emails(self):
        """
        Génération d'un modèle d'email unique pour l'échantillon via Google Gemini 1.5 Flash en utilisant la clé API de l'interface.
        """
        self.ensure_one()
        self._save_connection_params()
        
        api_key = self.gemini_api_key
        if not api_key:
            raise UserError(_("Veuillez renseigner votre Clé API Google Gemini dans l'onglet 'Connexion & API'."))

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}

        prompt = f"""
Tu es un expert en marketing digital et communication d'entreprise.
Rédige un e-mail professionnel et accrocheur en français pour une campagne marketing destinée à un échantillon ciblé.

Contexte de la campagne :
- Thème : {self.theme}
- Objectif / Description : {self.description or 'Présentation de nos services'}

Cible de l'échantillon :
- Région ciblée : {self.target_region or 'Toutes régions'}
- Domaine d'activité ciblé : {self.target_activity_domain or 'Tous secteurs'}

Instructions obligatoires :
1. Rédige un e-mail unique, persuasif et chaleureux, parfaitement adapté à ce segment cible.
2. Formate la réponse DIRECTEMENT en HTML propre (utilise des balises <p>, <br>, <strong>, etc. mais pas de balises <html> ou <body> ni de bloc markdown ```html).
3. Ajoute un objet d'e-mail pertinent sur la toute première ligne sous la forme : "OBJET: [Ton Objet]". Le corps de l'e-mail commencera après.
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            if response.status_code == 200:
                res_json = response.json()
                text_response = res_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                subject = f"Campagne : {self.theme}"
                body = text_response

                lines = text_response.split('\n')
                if lines and lines[0].startswith('OBJET:'):
                    subject = lines[0].replace('OBJET:', '').strip()
                    body = '\n'.join(lines[1:]).strip()

                self.write({
                    'generated_subject': subject,
                    'generated_body': body,
                    'state': 'ai_generated'
                })
            else:
                raise UserError(_("Erreur API Gemini (Code %s) : %s") % (response.status_code, response.text))

        except Exception as e:
            raise UserError(_("Erreur lors de la génération IA : %s") % str(e))

    def action_rephrase_email(self):
        """
        Envoie le corps actuel et l'instruction de reformulation à Gemini Flash.
        """
        self.ensure_one()
        self._save_connection_params()

        api_key = self.gemini_api_key
        if not api_key:
            raise UserError(_("Veuillez renseigner votre Clé API Google Gemini dans l'onglet 'Connexion & API'."))

        if not self.rephrase_prompt:
            raise UserError(_("Veuillez saisir une instruction de reformulation."))

        if not self.generated_body:
            raise UserError(_("Veuillez d'abord générer un e-mail initial avant de le reformuler."))

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}

        prompt = f"""
Tu es un expert en communication d'entreprise.
Voici un e-mail marketing existant :
{self.generated_body}

Voici l'instruction de l'utilisateur pour modifier cet e-mail :
"{self.rephrase_prompt}"

Applique l'instruction et renvoie le nouvel e-mail DIRECTEMENT en HTML propre (sans balises <html>, <body>, ni bloc markdown ```html).
"""
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
            if response.status_code == 200:
                res_json = response.json()
                text_response = res_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                
                self.write({
                    'generated_body': text_response,
                    'state': 'ai_generated'
                })
            else:
                raise UserError(_("Erreur API Gemini (Code %s) : %s") % (response.status_code, response.text))

        except Exception as e:
            raise UserError(_("Erreur lors de la reformulation IA : %s") % str(e))

    def action_confirm_campaign(self):
        self.state = 'ready'

    def action_send_campaign(self):
        """
        Envoi effectif de l'email unique à tous les contacts de l'échantillon.
        """
        self.ensure_one()
        if not self.generated_body:
            raise UserError(_("Le corps de l'e-mail est vide. Veuillez générer ou rédiger un e-mail avant l'envoi."))

        for line in self.contact_line_ids:
            if line.email:
                mail_values = {
                    'subject': self.generated_subject or self.name,
                    'body_html': self.generated_body,
                    'email_to': line.email,
                    'auto_delete': False,
                }
                self.env['mail.mail'].sudo().create(mail_values).send()
                line.state = 'sent'
        self.state = 'done'
