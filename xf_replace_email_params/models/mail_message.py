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
                        
                        # Log the filter and values for debugging purposes
                        _logger.info(f"Applying filter: {filter_condition} on values: {values}")
                        
                        # Compare the filter conditions directly with the values dictionary
                        if all(values.get(field) == value for field, value in filter_condition.items()):
                            _logger.info(f"Filter matched, updating emails for: {values}")
                            # Get replacement email if the filter matches
                            email_from, reply_to = rule.get_email_from_reply_to(model, company, internal_user)
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        raise ValidationError(f"Invalid filter condition: {e}")
        return super(MailMessage, self).create(values_list)