from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allowed_start_hour = fields.Float(
        string="Allowed Start Hour",
        config_parameter='calendar.allowed_start_hour'
    )
    allowed_end_hour = fields.Float(
        string="Allowed End Hour",
        config_parameter='calendar.allowed_end_hour'
    )
