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

    @api.depends('sales_period_days')
    def _compute_sales_metrics(self):
        for product in self:
            domain = [('product_id.product_tmpl_id', '=', product.id), ('state', 'in', ['sale', 'done'])]
            orders = self.env['sale.order.line'].search(domain)
            
            today = date.today()
            start_date = today - timedelta(days=product.sales_period_days)
            
            sales_data = {start_date + timedelta(days=i): 0 for i in range(product.sales_period_days)}
            
            for line in orders:
                order_date = line.order_id.date_order.date()
                if order_date in sales_data:
                    sales_data[order_date] += line.product_uom_qty
            
            daily_sales = list(sales_data.values())
            nonzero_sales = [qty for qty in daily_sales if qty > 0]
            total_period_days = product.sales_period_days
            
            total_sales = sum(daily_sales)
            product.avg_daily_sales = total_sales / total_period_days if total_period_days > 0 else 0
            product.max_daily_sales = max(daily_sales) if daily_sales else 0
            
            sorted_sales = sorted(daily_sales)  # Medián včetně nulových dnů
            sorted_nonzero_sales = sorted(nonzero_sales)  # Medián bez nulových dnů
            
            _logger.info("Sales data for %s: %s", product.name, sorted_sales)
            _logger.info("Nonzero Sales data for %s: %s", product.name, sorted_nonzero_sales)
            
            product.median_daily_sales = statistics.median(sorted_sales) if sorted_sales else 0
            product.median_nonzero_daily_sales = statistics.median(sorted_nonzero_sales) if sorted_nonzero_sales else 0
            
            # Lineární regrese - predikce budoucího prodeje
            x = np.arange(len(daily_sales))
            y = np.array(daily_sales)
            
            if len(x) > 1 and any(y):
                slope, intercept = np.polyfit(x, y, 1)
                predicted_value = slope * (len(x) + 1) + intercept
                product.predicted_daily_sales = max(0, predicted_value)  # Zajistí, že predikce není záporná
            else:
                product.predicted_daily_sales = 0

    def action_recompute_sales_metrics(self):
        self._compute_sales_metrics()
