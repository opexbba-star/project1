from odoo import fields, models


class EventQaQuestion(models.Model):
    """Une question soumise au Q&A en direct d'une session.

    Les questions arrivent en `pending` et doivent être `approved` par un
    modérateur avant d'apparaître sur la page publique ou la vue présentateur.
    Le compteur de votes est dénormalisé ; le contrôleur l'incrémente via
    sudo lorsqu'un utilisateur public vote.
    """
    _name = 'event.qa.question'
    _description = 'Question Q&A Évènement'
    _order = 'vote_count desc, create_date desc'

    track_id = fields.Many2one(
        comodel_name='event.track',
        string='Session',
        required=True,
        ondelete='cascade',
        index=True,
    )
    # Stocké related pour permettre filtrage/groupement par évènement
    event_id = fields.Many2one(
        comodel_name='event.event',
        related='track_id.event_id',
        store=True,
        index=True,
        string='Évènement',
    )
    author_name = fields.Char(
        string='Auteur',
        default='Anonyme',
    )
    question_text = fields.Text(
        string='Question',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('pending', 'En attente'),
            ('approved', 'Approuvée'),
            ('answered', 'Répondue'),
            ('rejected', 'Rejetée'),
        ],
        string='Statut',
        default='pending',
        required=True,
        index=True,
    )
    vote_count = fields.Integer(
        string='Votes',
        default=0,
        index=True,
    )

    # ------------------------------------------------------------------
    # Actions de modération
    # ------------------------------------------------------------------
    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_mark_answered(self):
        self.write({'state': 'answered'})

    def action_reset_pending(self):
        self.write({'state': 'pending'})
