
from odoo import models, fields, api

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    helpdesk_team_id = fields.Many2one('helpdesk.team', string="Helpdesk Team", ondelete='set null')

    @api.onchange('helpdesk_team_id')
    def _onchange_helpdesk_team_id(self):
        if self.helpdesk_team_id:
            self.team_members_ids = [(6, 0, self.helpdesk_team_id.member_ids.ids)]

    def write(self, vals):
        res = super().write(vals)
        if 'helpdesk_team_id' in vals and vals['helpdesk_team_id']:
            for team in self:
                team.team_members_ids = [(6, 0, team.helpdesk_team_id.member_ids.ids)]
        return res

    @api.model
    def create(self, vals):
        team = super().create(vals)
        if vals.get('helpdesk_team_id'):
            team.team_members_ids = [(6, 0, team.helpdesk_team_id.member_ids.ids)]
        return team
