class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def create(self, vals):
        if not vals.get('team_id') and vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            if partner.project_team_id:
                team = self.env['helpdesk.team'].search([
                    ('project_team_id', '=', partner.project_team_id.id)
                ], limit=1)
                if team:
                    vals['team_id'] = team.id
        return super().create(vals)