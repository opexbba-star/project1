from odoo import http
from odoo.http import request

class CourseAccessController(http.Controller):

    @http.route(['/slides/<model("slide.channel"):channel>'], type='http', auth='user', website=True)
    def slide_channel_overview(self, channel, **kwargs):
        user = request.env.user

        # Free course → redirect safely
        if channel.x_points_cost <= 0:
            return request.redirect(f"/slides/{channel.id}")

        # Already purchased → redirect safely
        if channel in user.x_purchased_channel_ids:
            return request.redirect(f"/slides/{channel.id}")

        # Not purchased → check points
        can_buy = user.x_points >= channel.x_points_cost

        return request.render("website_adherent.template_channel_locked", {
            'channel': channel,
            'can_buy': can_buy,
            'missing': channel.x_points_cost - user.x_points
        })

    @http.route(['/course/unlock/<int:channel_id>'], type='http', auth='user', website=True)
    def unlock_course(self, channel_id, **kwargs):
        channel = request.env['slide.channel'].browse(channel_id)
        user = request.env.user

        if not channel.exists():
            return request.not_found()

        # Free course → redirect safely
        if channel.x_points_cost <= 0:
            return request.redirect(f"/slides/{channel.id}")

        # Already purchased → redirect safely
        if channel in user.x_purchased_channel_ids:
            return request.redirect(f"/slides/{channel.id}")

        # Not enough points → redirect to slug with error
        if user.x_points < channel.x_points_cost:
            return request.redirect(f"/slides/{channel.website_url}?error=notenough")

        # Deduct points + unlock
        user.write({
            'x_points': user.x_points - channel.x_points_cost,
            'x_purchased_channel_ids': [(4, channel.id)]
        })

        return request.redirect(f"/slides/{channel.id}")
