from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    x_is_adherent = fields.Boolean(string="Adhérent", default=False)
    x_points = fields.Integer(string="Points", default=0)
    x_requested_points = fields.Integer(string="Requested Points", default=0)

    x_purchased_channel_ids = fields.Many2many(
        'slide.channel',
        string="Purchased Courses"
    )

    @api.model
    def create(self, vals):
        """Give +20 welcome points to every newly created user."""
        user = super(ResUsers, self).create(vals)

        # Give points only if user created by signup (not via backend import or admin)
        if not self.env.context.get('install_mode') and not self.env.context.get('no_welcome_points'):
            user.x_points += 20

        return user

    def action_accept_points(self):
        template = self.env.ref('website_adherent.mail_template_approve_points')
        for user in self:
            if user.x_requested_points > 0:
                user.x_points += user.x_requested_points
                user.x_requested_points = 0
                if template:
                    template.sudo().send_mail(user.id, force_send=True)
