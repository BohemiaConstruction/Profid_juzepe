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

    def action_close_task(self):
        for task in self:
            if task.sale_line_id:
                task.sale_line_id.qty_delivered += task.total_unit_qty
        return super(ProjectTask, self).action_close_task()
