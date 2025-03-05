from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, values_list):
        block_messages = []
        for values in values_list:
            if values.get("mail_message_id"):
                rules = self.env["mail.replace.rule"].search([])
                for rule in rules:
                    # Kontrolujeme, zda bylo pravidlo uplatněno už v mail.message
                    if rule.block_sending:
                        if values.get("mail_message_id") not in block_messages:
                            block_messages.append(values.get("mail_message_id"))

        mails = super(MailMail, self).create(values_list)
        if block_messages:
            mails_to_cancel = self.env["mail.mail"].search([("mail_message_id", "in", block_messages)])
            if mails_to_cancel:
                mails_to_cancel.sudo().write({"state": "cancel"})
                _logger.info(f"Blocking email sending for mail: {mails_to_cancel.mapped('mail_message_id')}")
                return self.env['mail.mail']

        return mails
