from odoo import models, fields, api
from datetime import timedelta, date
import statistics
import logging
import numpy as np

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    avg_daily_sales = fields.Float(string="Average Daily Sales", compute="_compute_sales_metrics", store=True)
    median_daily_sales = fields.Float(string="Median Daily Sales (All Days)", compute="_compute_sales_metrics", store=True)
    median_nonzero_daily_sales = fields.Float(string="Median Daily Sales (Non-Zero Days)", compute="_compute_sales_metrics", store=True)
    max_daily_sales = fields.Float(string="Max Daily Sales", compute="_compute_sales_metrics", store=True)
    predicted_daily_sales = fields.Float(string="Predicted Daily Sales (Linear Fit)", compute="_compute_sales_metrics", store=True)
    sales_period_days = fields.Integer(string="Sales Period (Days)", default=30)

    fastest_lead_delay = fields.Float(string="Fastest Lead Time", compute="_compute_fastest_lead_time", store=True)
    fsbnp = fields.Float(string="Forecasted Sales before next Purchase", compute="_compute_fsbnp", store=True)
    forecasted_with_sales = fields.Float(string="Forecasted with Sales", compute="_compute_forecasted_with_sales", store=True)

    @api.depends('sales_period_days', 'product_variant_ids.sale_order_ids.order_line.product_uom_qty')
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

            sales_data = {start_date + timedelta(days=i): 0 for i in range(product.sales_period_days)}
            
            for line in order_lines:
                order_date = line.order_id.date_order.date()
                if order_date in sales_data:
                    sales_data[order_date] += line.product_uom_qty
            
            daily_sales = list(sales_data.values())
            nonzero_sales = [qty for qty in daily_sales if qty > 0]
            total_period_days = product.sales_period_days
            
            product.avg_daily_sales = sum(daily_sales) / total_period_days if total_period_days > 0 else 0
            product.max_daily_sales = max(daily_sales) if daily_sales else 0
            product.median_daily_sales = statistics.median(daily_sales) if daily_sales else 0
            product.median_nonzero_daily_sales = statistics.median(nonzero_sales) if nonzero_sales else 0
            
            # Lineární regrese - predikce budoucího prodeje
            x = np.arange(len(daily_sales))
            y = np.array(daily_sales)
            
            if len(x) > 1 and any(y):
                slope, intercept = np.polyfit(x, y, 1)
                predicted_value = slope * (len(x) + 1) + intercept
                product.predicted_daily_sales = max(0, predicted_value)
            else:
                product.predicted_daily_sales = 0

    @api.depends('product_variant_ids.seller_ids.delay')
    def _compute_fastest_lead_time(self):
        for product in self:
            lead_times = product.product_variant_ids.mapped('seller_ids.delay')
            product.fastest_lead_delay = min(lead_times) if lead_times else 0

    @api.depends('avg_daily_sales', 'fastest_lead_delay')
    def _compute_fsbnp(self):
        for product in self:
            product.fsbnp = product.avg_daily_sales * product.fastest_lead_delay

    @api.depends('fsbnp', 'product_variant_ids.virtual_available')
    def _compute_forecasted_with_sales(self):
        for product in self:
            virtual_available = sum(product.product_variant_ids.mapped('virtual_available'))
            product.forecasted_with_sales = virtual_available - product.fsbnp

    def action_recompute_sales_metrics(self):
        self._compute_sales_metrics()
        self._compute_fastest_lead_time()
        self._compute_fsbnp()
        self._compute_forecasted_with_sales()

    def _cron_recompute_sales_metrics(self):
        products = self.search([])
        products._compute_sales_metrics()
        products._compute_fastest_lead_time()
        products._compute_fsbnp()
        products._compute_forecasted_with_sales()
