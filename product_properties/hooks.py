from odoo import api, SUPERUSER_ID

def cleanup_database_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['cleanup.database'].run_cleanup()
