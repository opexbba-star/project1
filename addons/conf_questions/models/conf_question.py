from odoo import models, fields


class ConfQuestion(models.Model):
    _name = 'conf.question'
    _description = 'Conference Question'
    _order = 'submitted_at asc'

    event_id = fields.Many2one(
        'conf.event', string='Événement', required=True, ondelete='cascade', index=True
    )
    submitter_name = fields.Char(string='Prénom', required=True)
    question_text = fields.Text(string='Question', required=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('read', 'Traitée'),
        ('skipped', 'Skippée'),
    ], string='État', default='pending', index=True)
    submitted_at = fields.Datetime(
        string='Soumise le', default=fields.Datetime.now, readonly=True
    )
