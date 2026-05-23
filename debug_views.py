import xmlrpc.client
import json

def debug_views():
    url = 'http://localhost:8069'
    db = 'odoo' # Wait, the user previously got `database "odoo" does not exist`. 
    # Let me read the odoo config from the docker container to find the DB name
    pass
