import traceback

try:
    View = env['ir.ui.view']
    parent_view = env.ref('ceo_campaign_automation.view_partner_form_dynamic_fields')
    print("Parent view:", parent_view.id)
    
    partner_model = env['ir.model']._get('res.partner')
    custom_fields = env['ir.model.fields'].search([
        ('model_id', '=', partner_model.id),
        ('name', '=like', 'x_%'),
        ('state', '=', 'manual'),
    ])
    print("Custom fields:", custom_fields.mapped('name'))
    
    arch_body = ""
    for cfield in custom_fields:
        arch_body += f'<field name="{cfield.name}"/>\n'
        
    arch = f'''<?xml version="1.0"?>
    <data>
        <xpath expr="//page[@name='ai_imported_fields']/group[@name='dynamic_fields_group']" position="inside">
            {arch_body}
        </xpath>
    </data>
    '''
    
    dynamic_view = View.search([('name', '=', 'res.partner.dynamic.ai.fields')], limit=1)
    if dynamic_view:
        print("Writing to existing view:", dynamic_view.id)
        dynamic_view.write({'arch': arch})
    else:
        print("Creating new view")
        dynamic_view = View.create({
            'name': 'res.partner.dynamic.ai.fields',
            'type': 'form',
            'model': 'res.partner',
            'inherit_id': parent_view.id,
            'arch': arch,
        })
        print("Created new view:", dynamic_view.id)
        
    env.registry.clear_cache()
    print("Success")
except Exception as e:
    traceback.print_exc()
