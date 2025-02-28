from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            if values.get("mail_message_id"):
                message = self.env["mail.message"].browse(values["mail_message_id"])
                rules = self.env["mail.replace.rule"].search([])

                for rule in rules:
                    # Kontrolujeme, zda bylo pravidlo uplatněno už v mail.message
                    if getattr(message, "apply_rule", False):  # Používáme flag z mail.message
                        if rule.block_sending:
                            _logger.info(f"Blocking email sending for mail: {values.get('mail_message_id')}")
                            values["state"] = "cancel"  # Zrušíme e-mail
                            break  # Ukončíme kontrolu, protože blokování je dostatečné

        return super(MailMail, self).create(values_list)
