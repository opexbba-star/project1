# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    x_points_cost = fields.Integer(
        string="Required Points",
        default=0,
        help="Number of points required for a user to enroll in this course."
    )

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    @api.model
    def create(self, vals):
        """
        Before creating the enrollment (attendee) record:
         - check the related course cost (channel.x_points)
         - find the user linked to partner_id (if any)
         - if user has insufficient points -> raise error
         - otherwise subtract points from user (atomic)
        """
        channel_id = vals.get('channel_id')
        partner_id = vals.get('partner_id')

        if channel_id and partner_id:
            channel = self.env['slide.channel'].browse(channel_id)
            cost = int(channel.x_points or 0)
            if cost > 0:
                # Find a user linked to this partner (portal/odoo user)
                user = self.env['res.users'].search([('partner_id', '=', partner_id)], limit=1)
                if not user:
                    # If no internal user, we may want to check partner-based points instead.
                    # For now we refuse so admin knows to convert to a user or handle differently.
                    raise UserError(_("You must have an Odoo user account to enroll with points."))
                # Check enough points
                if user.x_points < cost:
                    raise UserError(_("You need %s points to enroll in '%s' but you have %s points.") %
                                    (cost, channel.name, user.x_points))
                # Deduct points (keep it simple & atomic in the same transaction)
                user.x_points = user.x_points - cost

        return super(SlideChannelPartner, self).create(vals)
