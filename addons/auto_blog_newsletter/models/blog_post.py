from odoo import api, fields, models

class BlogPost(models.Model):
    _inherit = 'blog.post'

    @api.model
    def create(self, vals):
        post = super().create(vals)
        post._auto_send_newsletter()
        return post

    def write(self, vals):
        result = super().write(vals)
        if 'is_published' in vals and vals['is_published'] is True:
            self._auto_send_newsletter()
        return result

    def _auto_send_newsletter(self):
        for post in self:
            # Send only if published
            if not post.is_published:
                continue

            # Check if post belongs to "News" blog
            if post.blog_id.name != 'News':
                continue

            # Find contacts in Newsletter list
            mailing_list = self.env['mailing.list'].search([('name', '=', 'Newsletter')], limit=1)
            if not mailing_list:
                return

            contacts = mailing_list.contact_ids

            # Loop through subscribers
            for contact in contacts:
                notification_values = {
                    'subject': f"📰 New Blog Post: {post.name}",
                    'body_html': f"""
                        <p>Hello,</p>
                        <p>We just published a new article: <strong>{post.name}</strong></p>
                        <p>{post.teaser or ''}</p>
                        <p><a href="{post.website_url}">Click here to read the full article</a></p>
                    """,
                    'email_to': contact.email,
                    'email_from': self.env.user.company_id.email or 'noreply@example.com',
                    'auto_delete': True,
                }
                mail = self.env['mail.mail'].sudo().create(notification_values)
                mail.send()
