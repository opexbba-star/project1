
from odoo import api, fields, models

class InspectGroups(models.TransientModel):
    _name = 'inspect.groups'

    def run_inspection(self):
        groups_model = self.env['res.groups']
        fields_list = list(groups_model._fields.keys())
        print(f"DEBUG: Fields in res.groups: {fields_list}")
