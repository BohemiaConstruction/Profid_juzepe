
from odoo import models, fields, api

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    project_team_id = fields.Many2one('crm.team', string="Project Team", domain="[('type_team','=','project')]", ondelete='set null')

    @api.onchange('project_team_id')
    def _onchange_project_team_id(self):
        if self.project_team_id:
            self.member_ids = [(6, 0, self.project_team_id.team_members_ids.ids)]

    def write(self, vals):
        res = super().write(vals)
        if 'project_team_id' in vals and vals['project_team_id']:
            for team in self:
                team.member_ids = [(6, 0, team.project_team_id.team_members_ids.ids)]
        return res

    @api.model
    def create(self, vals):
        team = super().create(vals)
        if vals.get('project_team_id'):
            team.member_ids = [(6, 0, team.project_team_id.team_members_ids.ids)]
        return team
