from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    project_team_id = fields.Many2one(
        'crm.team',
        string='Project Team',
        domain=[('type_team', '=', 'project')]
    )