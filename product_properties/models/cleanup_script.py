from odoo import models, api

class CleanupDatabase(models.Model):
    _name = 'cleanup.database'
    _description = 'Cleanup Database for Duplicates'

    @api.model
    def cleanup_ir_model_fields_selection(self):
        self.env.cr.execute("""
            DELETE FROM ir_model_fields_selection
            WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER (PARTITION BY name ORDER BY id) AS row_num
                    FROM ir_model_fields_selection
                ) AS duplicates
                WHERE row_num > 1
            )
        """)

    @api.model
    def cleanup_ir_model_data(self):
        self.env.cr.execute("""
            DELETE FROM ir_model_data WHERE module = 'product_properties_fixed_corrected';
        """)

    @api.model
    def run_cleanup(self):
        self.cleanup_ir_model_fields_selection()
        self.cleanup_ir_model_data()
        return True
