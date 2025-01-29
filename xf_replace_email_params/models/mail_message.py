from odoo import models, api

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
            message_type = values.get('message_type', '')
            domain = [
                ('model', '=', values.get('model')),
                ('company_id', '=', values.get('company_id')),
                ('only_for_internal_users', '=', values.get('only_for_internal_users'))
            ]
            if message_type:
                domain.append(('message_type_filter', '=', message_type))
            
            rules = self.env['mail.replace.rule'].search(domain)
            for rule in rules:
                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, dict):
                            raise ValidationError("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                        
                        for field, value in filter_condition.items():
                            if 'res_id' in values:
                                related_record = self.env[values.get('model')].browse(values.get('res_id'))
                                field_value = getattr(related_record, field, None)
                                if isinstance(field_value, models.BaseModel):
                                    field_value = field_value.id  
                                _logger.info(f"Checking {field} (value: {field_value}) against {value}")
                                
                                if field_value != value:
                                    _logger.info(f"Field {field} does not match filter. Skipping update.")
                                    break
                            else:
                                _logger.warning(f"res_id not found in values: {values}")
                                continue
                        else:
                            _logger.info(f"Filter matched, updating emails for: {values}")
                            email_from, reply_to = rule.get_email_from_reply_to(values.get('model'), values.get('company_id'), values.get('only_for_internal_users'))
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        raise ValidationError(f"Invalid filter condition: {e}")
                else:
                    _logger.info(f"No domain filter set. Updating emails for: {values}")
                    email_from, reply_to = rule.get_email_from_reply_to(values.get('model'), values.get('company_id'), values.get('only_for_internal_users'))
                    if email_from:
                        values.update({'email_from': email_from})
                    if reply_to is not None:
                        values.update({'reply_to': reply_to})
        
        return super(MailMessage, self).create(values_list)