
from odoo import models, fields, api
from datetime import timedelta, date
import statistics
import logging
import numpy as np

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    avg_weekly_sales = fields.Float(string="Average Weekly Sales", compute="_compute_sales_metrics", store=True)
    median_weekly_sales = fields.Float(string="Median Weekly Sales (All Weeks)", compute="_compute_sales_metrics", store=True)
    median_nonzero_weekly_sales = fields.Float(string="Median Weekly Sales (Non-Zero Weeks)", compute="_compute_sales_metrics", store=True)
    max_weekly_sales = fields.Float(string="Max Weekly Sales", compute="_compute_sales_metrics", store=True)
    predicted_weekly_sales = fields.Float(string="Predicted Weekly Sales (Linear Fit)", compute="_compute_sales_metrics", store=True)
    sales_period_days = fields.Integer(string="Sales Period History (Days)", default=90)

    fastest_lead_delay = fields.Float(string="Fastest Lead Time", compute="_compute_fastest_lead_time", store=True)
    fsbnp = fields.Float(string="Forecasted Sales before next Purchase", compute="_compute_fsbnp", store=True)
    forecasted_with_sales = fields.Float(string="Forecasted with Sales", compute="_compute_forecasted_with_sales", store=True)

    @api.depends('sales_period_days')
    def _compute_sales_metrics(self):
        today = date.today()
        for product in self:
            start_date = today - timedelta(days=product.sales_period_days)
            domain = [
                ('order_id.date_order', '>=', start_date),
                ('order_id.state', 'in', ['sale', 'done']),
                ('product_id', 'in', product.product_variant_ids.ids)
            ]
            order_lines = self.env['sale.order.line'].search(domain)

            num_weeks = product.sales_period_days // 7
            weekly_sales_data = {i: 0 for i in range(num_weeks)}

            for line in order_lines:
                order_date = line.order_id.date_order.date()
                if order_date >= start_date:
                    week_index = (order_date - start_date).days // 7
                    if week_index in weekly_sales_data:
                        weekly_sales_data[week_index] += line.product_uom_qty

            weekly_sales = list(weekly_sales_data.values())
            nonzero_weekly_sales = [qty for qty in weekly_sales if qty > 0]

            total_weeks = len(weekly_sales)

            product.avg_weekly_sales = sum(weekly_sales) / total_weeks if total_weeks > 0 else 0
            product.max_weekly_sales = max(weekly_sales) if weekly_sales else 0
            product.median_weekly_sales = statistics.median(weekly_sales) if weekly_sales else 0
            product.median_nonzero_weekly_sales = statistics.median(nonzero_weekly_sales) if nonzero_weekly_sales else 0

            # Lineární regrese - predikce budoucího prodeje
            x = np.arange(len(weekly_sales))
            y = np.array(weekly_sales)

            if len(x) > 1 and any(y):
                slope, intercept = np.polyfit(x, y, 1)
                predicted = slope * (len(weekly_sales) + 1) + intercept
                product.predicted_weekly_sales = max(predicted, 0)
            else:
                product.predicted_weekly_sales = 0
