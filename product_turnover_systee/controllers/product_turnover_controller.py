from odoo import http
from odoo.http import request
from datetime import timedelta, date

class ProductTurnoverController(http.Controller):
    @http.route('/product_turnover/data/<int:product_id>', type='json', auth='public')
    def get_product_sales_data(self, product_id):
        product = request.env['product.template'].browse(product_id)

        if not product:
            return {}

        sales_period_days = product.sales_period_days
        today = date.today()
        start_date = today - timedelta(days=sales_period_days)

        sales_data = {start_date + timedelta(days=i): 0 for i in range(sales_period_days)}
        orders = request.env['sale.order.line'].search([
            ('product_id.product_tmpl_id', '=', product.id),
            ('state', 'in', ['sale', 'done'])
        ])

        for line in orders:
            order_date = line.order_id.date_order.date()
            if order_date in sales_data:
                sales_data[order_date] += line.product_uom_qty

        dates = list(sales_data.keys())
        values = list(sales_data.values())

        return {'dates': [str(d) for d in dates], 'sales': values}
