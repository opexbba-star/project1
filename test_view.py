try:
    View = env['ir.ui.view']
    parent = env.ref('ceo_campaign_automation.view_partner_form_dynamic_fields')
    print("PARENT:", parent)
    fields = env['ir.model.fields'].search([('model', '=', 'res.partner'), ('state', '=', 'manual')])
    print("FIELDS:", fields.mapped('name'))
    wizard = env['campaign.import.wizard'].create({'file_data': b''})
    wizard._update_partner_form_view()
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
