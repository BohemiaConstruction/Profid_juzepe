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

    avg_weekly_stock_out = fields.Float(string="Avg Weekly Stock OUT", compute="_compute_stock_metrics", store=True)
    median_weekly_stock_out = fields.Float(string="Median Weekly Stock OUT", compute="_compute_stock_metrics", store=True)
    max_weekly_stock_out = fields.Float(string="Max Weekly Stock OUT", compute="_compute_stock_metrics", store=True)
    predicted_weekly_stock_out = fields.Float(string="Predicted Weekly Stock OUT (Linear)", compute="_compute_stock_metrics", store=True)

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
            _logger.debug(f"[%s] Searching order moves: domain=%s", product.name, domain)
            order_lines = self.env['sale.order.line'].search(domain)
            _logger.debug(f"[%s] Found %d orders", product.name, len(order_lines))

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

            x = np.arange(len(weekly_sales))
            y = np.array(weekly_sales)

            if len(x) > 1 and any(y):
                slope, intercept = np.polyfit(x, y, 1)
                predicted = slope * (len(weekly_sales) + 1) + intercept
                product.predicted_weekly_sales = max(predicted, 0)
            else:
                product.predicted_weekly_sales = 0

    @api.depends('sales_period_days')
    def _compute_stock_metrics(self):
        print(">>> _compute_stock_metrics() CALLED")
        _logger.warning(f"Self obsahuje {len(self)} produktů")
        today = date.today()
        for product in self:
            _logger.warning(f"Produkt: {product.name}")
            _logger.warning(f"Varianty: {product.product_variant_ids.ids}")
            start_date = today - timedelta(days=product.sales_period_days)
            domain = [
                ('product_id', 'in', product.product_variant_ids.ids),
                ('state', '=', 'done'),
                ('date', '>=', start_date),
                '|',
                ('location_dest_id.usage', '=', 'customer'),      # výdej
                ('location_dest_id.usage', '=', 'production')     # spotřeba ve výrobě
            ]
            _logger.warning(f"Doména stock move: {domain}")
            _logger.debug(f"[%s] Searching stock moves: domain=%s", product.name, domain)
            stock_moves = self.env['stock.move'].search(domain)
            _logger.debug(f"[%s] Found %d stock moves", product.name, len(stock_moves))
            num_weeks = product.sales_period_days // 7
            weekly_data = {i: 0 for i in range(num_weeks)}

            for move in stock_moves:
                move_date = move.date.date()
                if move_date >= start_date:
                    week_index = (move_date - start_date).days // 7
                    if week_index in weekly_data:
                        weekly_data[week_index] += move.product_uom_qty

            weekly_vals = list(weekly_data.values())
            nonzero_vals = [v for v in weekly_vals if v > 0]
            total_weeks = len(weekly_vals)

            product.avg_weekly_stock_out = sum(weekly_vals) / total_weeks if total_weeks > 0 else 0
            product.max_weekly_stock_out = max(weekly_vals) if weekly_vals else 0
            product.median_weekly_stock_out = statistics.median(weekly_vals) if weekly_vals else 0

            x = np.arange(len(weekly_vals))
            y = np.array(weekly_vals)

            if len(x) > 1 and any(y):
                slope, intercept = np.polyfit(x, y, 1)
                predicted = slope * (len(weekly_vals) + 1) + intercept
                product.predicted_weekly_stock_out = max(predicted, 0)
            else:
                product.predicted_weekly_stock_out = 0

    @api.depends('product_variant_ids.seller_ids.delay')
    def _compute_fastest_lead_time(self):
        for product in self:
            lead_times = product.product_variant_ids.mapped('seller_ids.delay')
            product.fastest_lead_delay = min(lead_times) if lead_times else 0

    @api.depends('avg_weekly_sales', 'fastest_lead_delay')
    def _compute_fsbnp(self):
        for product in self:
            product.fsbnp = product.avg_weekly_sales * (product.fastest_lead_delay / 7.0)

    @api.depends('fsbnp', 'product_variant_ids.virtual_available')
    def _compute_forecasted_with_sales(self):
        for product in self:
            virtual_available = sum(product.product_variant_ids.mapped('virtual_available'))
            product.forecasted_with_sales = virtual_available - product.fsbnp

    def action_recompute_sales_metrics(self):
        _logger.info(f"Manual recompute called for %s", self.name)
        for product in self:
            product._compute_sales_metrics()
            product._compute_stock_metrics()
            product._compute_fastest_lead_time()
            product._compute_fsbnp()
            product._compute_forecasted_with_sales()

    def _cron_recompute_sales_metrics(self):
        products = self.search([])
        products._compute_sales_metrics()
        products._compute_stock_metrics()
        products._compute_fastest_lead_time()
        products._compute_fsbnp()
        products._compute_forecasted_with_sales()

class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_recompute_sales_metrics(self):
        for template in self.mapped('product_tmpl_id'):
            template.action_recompute_sales_metrics()
