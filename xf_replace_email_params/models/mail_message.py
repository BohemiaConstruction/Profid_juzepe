from odoo import models, api
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

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            author_partner_id = values.get('author_id', False)
            model = values.get('model', False)
            user = self.get_author_user(author_partner_id)
            company = user and user.company_id
            internal_user = user and user.has_group('base.group_user')

            # Fetch the rule(s) based on model, company, and internal user
            rules = self.env['mail.replace.rule'].search([
                ('model', '=', model),
                ('company_id', '=', company.id),
                ('only_for_internal_users', '=', internal_user)
            ])

            for rule in rules:
                # Evaluate domain filter dynamically from the rule
                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, dict):
                            raise ValidationError("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                        
                        # Iterate over each field in the domain filter and compare values
                        for field, value in filter_condition.items():
                            # Retrieve the value of the field from the related model
                            if 'res_id' in values:
                                related_record = self.env[model].browse(values.get('res_id'))
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
                            email_from, reply_to = rule.get_email_from_reply_to(model, company, internal_user)
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})

                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        raise ValidationError(f"Invalid filter condition: {e}")
        return super(MailMessage, self).create(values_list)