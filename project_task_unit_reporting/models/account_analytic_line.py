from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    unit_qty = fields.Float(
        string="Units",
        default=0.0,
        help="Number of units completed during this timesheet entry."
    )
