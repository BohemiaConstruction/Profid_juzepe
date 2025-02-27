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
                    if rule.message_type_filter and rule.message_type_filter != message.message_type:
                        continue
                    if rule.domain_filter:
                        try:
                            filter_condition = eval(rule.domain_filter)
                            if not isinstance(filter_condition, dict):
                                _logger.warning("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                                continue

                            for field, value in filter_condition.items():
                                related_record = message.env[message.model].browse(message.res_id)
                                field_value = getattr(related_record, field, None)
                                if isinstance(field_value, models.BaseModel):
                                    field_value = field_value.id  
                                if field_value != value:
                                    break
                            else:
                                if rule.block_sending:
                                    _logger.info(f"Blocking email sending for mail: {values.get('mail_message_id')}")
                                    values["state"] = "cancel"  # Zrušíme e-mail
                        except Exception as e:
                            _logger.error(f"Error applying filter: {e}")
                            continue

        return super(MailMail, self).create(values_list)
