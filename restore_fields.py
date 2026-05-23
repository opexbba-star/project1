import xmlrpc.client

def restore_fields():
    url = 'http://localhost:8069'
    db = 'opexbba-star'
    username = 'admin'
    password = '2'
    
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    # Get all custom fields we created
    custom_fields = models.execute_kw(db, uid, password, 'ir.model.fields', 'search_read',
        [[('model', '=', 'res.partner'), ('state', '=', 'manual'), ('name', '=like', 'x_%')]],
        {'fields': ['name']}
    )
    
    # We will trigger the wizard's update view function for each field to ensure it is in the view.
    for cf in custom_fields:
        print("Restoring:", cf['name'])
        # Call the wizard model method directly via execute_kw
        models.execute_kw(db, uid, password, 'campaign.import.wizard', '_update_partner_form_view', [[], cf['name']])

if __name__ == '__main__':
    restore_fields()
