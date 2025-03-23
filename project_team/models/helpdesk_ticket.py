from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    @api.model
    def create(self, vals):
        _logger.info("🛠 CREATE Helpdesk Ticket: vals = %s", vals)

        if not vals.get('team_id') and vals.get('partner_id'):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            _logger.info("🧍 Partner: %s | Project Team: %s", partner.name, partner.project_team_id)

            if partner.project_team_id:
                team = self.env['helpdesk.team'].search([
                    ('project_team_id', '=', partner.project_team_id.id)
                ], limit=1)
                _logger.info("🔎 Found Helpdesk Team: %s", team.name if team else 'None')

                if team:
                    vals['team_id'] = team.id
                    _logger.info("✅ Assigned team_id = %s", team.id)

        return super().create(vals)