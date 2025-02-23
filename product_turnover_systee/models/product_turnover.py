from odoo import models, fields, api
from datetime import timedelta, date
import statistics

class ProductProduct(models.Model):
    _inherit = "product.product"

    avg_daily_sales = fields.Float(string="Average Daily Sales", compute="_compute_sales_metrics", store=True)
    median_daily_sales = fields.Float(string="Median Daily Sales", compute="_compute_sales_metrics", store=True)
    max_daily_sales = fields.Float(string="Max Daily Sales", compute="_compute_sales_metrics", store=True)
    sales_period_days = fields.Integer(string="Sales Period (Days)", default=30)

    @api.depends('sales_period_days')
    def _compute_sales_metrics(self):
        for product in self:
            domain = [('product_id', '=', product.id), ('state', 'in', ['sale', 'done'])]
            orders = self.env['sale.order.line'].search(domain)
            sales_data = {}
            
            today = date.today()
            start_date = today - timedelta(days=product.sales_period_days)
            
            for line in orders:
                order_date = line.order_id.date_order.date()
                if order_date >= start_date:
                    sales_data[order_date] = sales_data.get(order_date, 0) + line.product_uom_qty
            
            daily_sales = list(sales_data.values())
            total_period_days = product.sales_period_days
            
            total_sales = sum(daily_sales)
            product.avg_daily_sales = total_sales / total_period_days if total_period_days > 0 else 0
            product.max_daily_sales = max(daily_sales) if daily_sales else 0
            
            if daily_sales:
                product.median_daily_sales = statistics.median(daily_sales)
            else:
                product.median_daily_sales = 0

    def action_recompute_sales_metrics(self):
        self._compute_sales_metrics()

class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    avg_daily_sales = fields.Float(related="product_id.avg_daily_sales", string="Average Daily Sales", readonly=True)
    median_daily_sales = fields.Float(related="product_id.median_daily_sales", string="Median Daily Sales", readonly=True)
    max_daily_sales = fields.Float(related="product_id.max_daily_sales", string="Max Daily Sales", readonly=True)
    sales_period_days = fields.Integer(related="product_id.sales_period_days", string="Sales Period (Days)", readonly=True)

class ProductTurnoverCron(models.Model):
    _name = "product.turnover.cron"
    _description = "Scheduled Task for Product Turnover Calculation"

    @api.model
    def compute_product_turnover(self):
        products = self.env['product.product'].search([])
        products._compute_sales_metrics()
