from odoo import models, api


from odoo import models, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('partner_id'):
                partner = self.env['res.partner'].browse(vals['partner_id'])
                if partner.project_team_id:
                    team = self.env['helpdesk.team'].search([
                        ('project_team_id', '=', partner.project_team_id.id)
                    ], limit=1)
                    if team:
                        vals['team_id'] = team.id  # přepíše i pokud je vyplněno
        return super().create(vals_list)