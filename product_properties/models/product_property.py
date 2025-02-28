from odoo import models, fields

class ProductPropertyCategory(models.Model):
    _name = 'product.property.category'
    _description = 'Product Property Category'

    name = fields.Char(string='Category Name', required=True)

class ProductProperty(models.Model):
    _name = 'product.property'
    _description = 'Product Property'

    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    category_id = fields.Many2one('product.property.category', string='Category', required=True)
    part_number = fields.Char(string='Part Number', required=True)
    value = fields.Float(string='Value', required=True)
    unit = fields.Selection([], string='Unit')  # Dynamicky nastaveno dle kategorie
    voltage_rating_vdc = fields.Float(string='Voltage Rating [VDC]')
    dielectric = fields.Selection([
        ('C0G', 'C0G (NP0)'), ('X5R', 'X5R'), ('X7R', 'X7R'), ('X6S', 'X6S'), ('X7S', 'X7S'), ('X7T', 'X7T')
    ], string='Dielectric')
    tolerance = fields.Float(string='Tolerance [%]')
    footprint = fields.Selection([
        ('0201', '0201'), ('0402', '0402'), ('0603', '0603'), ('0805', '0805'),
        ('1206', '1206'), ('1210', '1210'), ('1216', '1216'), ('2010', '2010'), ('1812', '1812'), ('2220', '2220')
    ], string='Footprint', required=True)
    note = fields.Text(string='Note')

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_id = fields.Many2one('product.property', string='Technical Properties', ondelete='cascade')