from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    # Common Values
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    name = fields.Char(
        string='Rule Name',
        required=True,
    )
    model_id = fields.Many2one(
        string='Model',
        comodel_name='ir.model',
        ondelete='cascade',
    )
    model = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda self: self.env.company,
        ondelete='cascade',
        index=True,
    )
    only_for_internal_users = fields.Boolean(
        string='Only for Internal Users',
        default=True,
        help="If enabled, the rule only applies to internal users."
    )
    
    # New domain filter for model-based email replacements
    domain_filter = fields.Char(
        string="Domain Filter",
        help="Filter criteria for applying the rule, e.g., {'support_team': 1}, {'user_id': 5}."
    )
    
    from_email = fields.Char(
        string='FROM Email Address',
        help='Email address to be used in the FROM field.',
    )
    reply_email = fields.Char(
        string='REPLY Email Address',
        help='Email address to be used in the REPLY field.',
    )

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            # Get the message_type of the current message
            message_type = values.get('message_type', '')

            # Fetch the rule(s) based on model, company, internal user, and message_type
            domain = [
                ('model', '=', values.get('model')),
                ('company_id', '=', values.get('company_id')),
                ('only_for_internal_users', '=', values.get('only_for_internal_users'))
            ]

            # Filter the rules based on the message_type
            if message_type:
                domain.append(('message_type_filter', '=', message_type))

            rules = self.env['mail.replace.rule'].search(domain)

            for rule in rules:
                # If domain filter is set, evaluate the conditions
                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, dict):
                            raise ValidationError("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                        
                        # Iterate over each field in the domain filter and compare values
                        for field, value in filter_condition.items():
                            # Retrieve the value of the field from the related model
                            if 'res_id' in values:
                                related_record = self.env[values.get('model')].browse(values.get('res_id'))
                                field_value = getattr(related_record, field, None)

                                # If field is a relation (e.g., Many2one), retrieve the ID
                                if isinstance(field_value, models.BaseModel):
                                    field_value = field_value.id  # Get the ID of the related record

                                # Log the retrieved value for debugging
                                _logger.info(f"Checking {field} (value: {field_value}) against {value}")
                                
                                # Check if the field value matches the filter value
                                if field_value != value:
                                    _logger.info(f"Field {field} does not match filter. Skipping update.")
                                    break
                            else:
                                _logger.warning(f"res_id not found in values: {values}")
                                continue
                        else:
                            # If all conditions match, apply the email replacements
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
                    # If domain filter is not set, update the emails without filtering
                    _logger.info(f"No domain filter set. Updating emails for: {values}")
                    email_from, reply_to = rule.get_email_from_reply_to(values.get('model'), values.get('company_id'), values.get('only_for_internal_users'))
                    if email_from:
                        values.update({'email_from': email_from})
                    if reply_to is not None:
                        values.update({'reply_to': reply_to})

        return super(MailMessage, self).create(values_list)
