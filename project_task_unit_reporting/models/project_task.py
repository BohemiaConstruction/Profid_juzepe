from odoo import models, fields, api, exceptions

class ProjectTask(models.Model):
    _inherit = "project.task"

    total_unit_qty = fields.Float(
        string="Total Units",
        compute="_compute_total_unit_qty",
        store=True,
    )

    @api.depends("timesheet_ids.unit_qty")
    def _compute_total_unit_qty(self):
        for task in self:
            task.total_unit_qty = sum(task.timesheet_ids.mapped("unit_qty"))

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        sale_line_ids = self.mapped("sale_line_id")
        for sale_line in sale_line_ids:
            related_tasks = self.search([("sale_line_id", "=", sale_line.id)])
            total_delivered = sum(related_tasks.mapped("total_unit_qty"))
            sale_line.qty_delivered = total_delivered
        return res
