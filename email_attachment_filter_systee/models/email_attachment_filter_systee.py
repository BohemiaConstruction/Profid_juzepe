from odoo import models, fields

class EmailAttachmentFilterSettings(models.Model):
    _name = 'email.attachment.filter.settings'
    _description = 'Settings for Email Attachment Filter'

    is_active = fields.Boolean('Enable Attachment Filtering', default=True)
    min_attachment_size = fields.Integer('Minimum Attachment Size (KB)', default=100)

    @api.model
    def get_settings(self):
        settings = self.search([], limit=1)
        if not settings:
            settings = self.create({
                'is_active': True,
                'min_attachment_size': 100
            })
        return settings
