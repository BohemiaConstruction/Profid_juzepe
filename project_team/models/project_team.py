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

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    project_team_id = fields.Many2one('project.team', string="Project Team", ondelete='set null')

    @api.onchange('project_team_id')
    def _onchange_project_team_id(self):
        if self.project_team_id:
            self.member_ids = [(6, 0, self.project_team_id.member_ids.ids)]