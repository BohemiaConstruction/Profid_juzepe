from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    category_id = fields.Many2one('product.property.category', string='Property Category')
    part_number = fields.Char(string='Part Number', required=True)
    value = fields.Float(string='Value', required=True)
    unit = fields.Selection([
        ('pF', 'pF'), ('nF', 'nF'), ('μF', 'μF'), ('mΩ', 'mΩ'), ('Ω', 'Ω'), ('kΩ', 'kΩ'), ('MΩ', 'MΩ')
    ], string='Unit')
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