from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    pp_category_id = fields.Many2one('product.property.category', string='Property Category')
    pp_part_number = fields.Char(string='Part Number', required=True)
    pp_value = fields.Float(string='Value', required=True)
    pp_unit = fields.Selection([
        ('pF', 'pF'), ('nF', 'nF'), ('μF', 'μF'), ('mΩ', 'mΩ'), ('Ω', 'Ω'), ('kΩ', 'kΩ'), ('MΩ', 'MΩ')
    ], string='Unit')
    pp_voltage_rating_vdc = fields.Float(string='Voltage Rating [VDC]')
    pp_dielectric = fields.Selection([
        ('C0G', 'C0G (NP0)'), ('X5R', 'X5R'), ('X7R', 'X7R'), ('X6S', 'X6S'), ('X7S', 'X7S'), ('X7T', 'X7T')
    ], string='Dielectric')
    pp_tolerance = fields.Float(string='Tolerance [%]')
    PP_footprint = fields.Selection([
        ('0201', '0201'), ('0402', '0402'), ('0603', '0603'), ('0805', '0805'),
        ('1206', '1206'), ('1210', '1210'), ('1216', '1216'), ('2010', '2010'), ('1812', '1812'), ('2220', '2220')
    ], string='Footprint', required=True)
    pp_note = fields.Text(string='Note')