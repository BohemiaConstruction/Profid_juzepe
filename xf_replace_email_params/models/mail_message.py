from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def get_author_user(self, author_partner_id):
        if not author_partner_id:
            return
        partner = self.env['res.partner'].with_context(active_test=False).browse(author_partner_id)
        if partner and partner.user_ids:
            for user in partner.user_ids:
                return user

    @api.model_create_multi
    def create(self, values_list):
        messages = super(MailMessage, self).create(values_list)
        
        for message in messages:
            rules = self.env['mail.replace.rule'].search([])
            for rule in rules:
                if rule.message_type_filter and rule.message_type_filter != message.message_type:
                    continue

                # Pravidlo se aplikuje vždy, pokud je prázdný domain_filter nebo pokud odpovídá
                apply_rule = True

                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, dict):
                            _logger.warning("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                            continue

                        apply_rule = False  # Výchozí hodnota se změní, pokud podmínka projde
                        for field, value in filter_condition.items():
                            related_record = message.env[message.model].browse(message.res_id)
                            field_value = getattr(related_record, field, None)
                            if isinstance(field_value, models.BaseModel):
                                field_value = field_value.id  
                            if field_value == value:
                                apply_rule = True
                                break

                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        continue

                if apply_rule:
                    email_from, reply_to = rule.email_from_computed, rule.reply_to_computed
                    if email_from:
                        message.sudo().write({'email_from': email_from})
                    if reply_to:
                        message.sudo().write({'reply_to': reply_to})

                    # Pokud je aktivní block_sending, zpráva nebude odeslána
                    if rule.block_sending:
                        _logger.info(f"Blocking email sending for message: {message.id}")
                        self.env['mail.mail'].search([('mail_message_id', '=', message.id)]).sudo().write({'state': 'cancel'})

        return messages
    