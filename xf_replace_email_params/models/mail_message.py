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
        for values in values_list:
            author_partner_id = values.get('author_id', False)
            model = values.get('model', False)
            user = self.get_author_user(author_partner_id)
            company = user and user.company_id
            internal_user = user and user.has_group('base.group_user')

            rules = self.env['mail.replace.rule'].search([])
            for rule in rules:
                if rule.message_type_filter and rule.message_type_filter != values.get('message_type', ''):
                    continue
                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, dict):
                            _logger.warning("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                            continue

                        for field, value in filter_condition.items():
                            if 'res_id' in values:
                                related_record = self.env[values.get('model')].browse(values.get('res_id'))
                                field_value = getattr(related_record, field, None)
                                if isinstance(field_value, models.BaseModel):
                                    field_value = field_value.id  
                                if field_value != value:
                                    break
                        else:
                            if rule.discard_message:
                                _logger.info(f"Message discarded due to matching rule: {rule.name}")
                                return self.browse()  # Vrátíme prázdný recordset = zpráva se nevytvoří

                            email_from, reply_to = self.env['mail.replace.rule'].get_email_from_reply_to(model, company, internal_user)
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        continue

        return super(MailMessage, self).create(values_list)
