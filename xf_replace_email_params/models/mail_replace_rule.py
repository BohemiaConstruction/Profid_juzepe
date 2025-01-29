from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class MailReplaceRule(models.Model):
    _name = 'mail.replace.rule'
    _description = 'Email Replacement Rule'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    message_type_filter = fields.Selection(
        [
            ('email', 'Incoming Email'),
            ('comment', 'User Comment'),
            ('email_outgoing', 'Outgoing Email'),
            ('notification', 'System Notification'),
            ('auto_comment', 'Automated Comment'),
            ('user_notification', 'User Notification')
        ],
        string="Message Type Filter",
        default='email',
        help="Select which message type the rule applies to."
    )
    domain_filter = fields.Char(
        string="Domain Filter",
        help="Filter criteria in dictionary format (e.g., {'support_team': 1})."
    )

    @api.model
    def apply_rule(self, values):
        message_type = values.get('message_type', '')
        
        domain = [
            ('model', '=', values.get('model')),
            ('company_id', '=', values.get('company_id')),
            ('only_for_internal_users', '=', values.get('only_for_internal_users'))
        ]
        
        if message_type:
            domain.append(('message_type_filter', '=', message_type))
        
        rules = self.search(domain)
        
        for rule in rules:
            if rule.domain_filter:
                try:
                    filter_condition = eval(rule.domain_filter)
                    if not isinstance(filter_condition, dict):
                        raise ValidationError("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                    
                    for field, value in filter_condition.items():
                        if 'res_id' in values and values.get('model'):
                            related_record = self.env[values.get('model')].browse(values.get('res_id'))
                            field_value = getattr(related_record, field, None)

                            if isinstance(field_value, models.BaseModel):
                                field_value = field_value.id

                            _logger.info(f"Checking {field} (value: {field_value}) against {value}")

                            if field_value != value:
                                _logger.info(f"Field {field} does not match filter. Skipping update.")
                                break
                    else:
                        email_from, reply_to = rule.get_email_from_reply_to(
                            values.get('model'), values.get('company_id'), values.get('only_for_internal_users')
                        )
                        if email_from:
                            values.update({'email_from': email_from})
                        if reply_to is not None:
                            values.update({'reply_to': reply_to})
                except Exception as e:
                    _logger.error(f"Error applying filter: {e}")
                    raise ValidationError(f"Invalid filter condition: {e}")
            else:
                email_from, reply_to = rule.get_email_from_reply_to(
                    values.get('model'), values.get('company_id'), values.get('only_for_internal_users')
                )
                if email_from:
                    values.update({'email_from': email_from})
                if reply_to is not None:
                    values.update({'reply_to': reply_to})