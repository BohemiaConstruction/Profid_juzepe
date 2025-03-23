# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    members_ids = fields.Many2many('res.users', 'project_user_rel', 'project_id',
                                   'user_id', 'Project Members', help="""Project's
                               members are users who can have an access to
                               the tasks related to this project."""
                                   )
    team_id = fields.Many2one('crm.team', "Project Team",
                              domain=[('type_team', '=', 'project')])

    @api.onchange('team_id')
    def _get_team_members(self):
        self.update({"members_ids": [(6, 0, self.team_id.team_members_ids.ids)]})

    helpdesk_team_id = fields.Many2one('helpdesk.team', string="Helpdesk Team", ondelete='set null')

    @api.onchange('helpdesk_team_id')
    def _onchange_helpdesk_team_id(self):
        if self.helpdesk_team_id:
            self.member_ids = [(6, 0, self.helpdesk_team_id.member_ids.ids)]

    def write(self, vals):
        res = super().write(vals)
        if 'helpdesk_team_id' in vals and vals['helpdesk_team_id']:
            for team in self:
                team.member_ids = [(6, 0, team.helpdesk_team_id.member_ids.ids)]
        return res

    @api.model
    def create(self, vals):
        team = super().create(vals)
        if vals.get('helpdesk_team_id'):
            team.member_ids = [(6, 0, team.helpdesk_team_id.member_ids.ids)]
        return team

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
