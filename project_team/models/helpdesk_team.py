from odoo import fields, models

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    project_team_id = fields.Many2one(
        'crm.team',
        string="Project Team",
        domain=[('type_team', '=', 'project')],
    )