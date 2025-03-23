# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    project_team_id = fields.Many2one('project.team', string="Project Team", ondelete='set null')

    @api.onchange('project_team_id')
    def _onchange_project_team_id(self):
        if self.project_team_id:
            self.member_ids = [(6, 0, self.project_team_id.member_ids.ids)]