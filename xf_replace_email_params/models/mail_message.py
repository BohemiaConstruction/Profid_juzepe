from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def get_author_user(self, author_partner_id):
        if not author_partner_id:
            return None
        partner = self.env['res.partner'].with_context(active_test=False).browse(author_partner_id)
        if partner and partner.user_ids:
            for user in partner.user_ids:
                return user

    @api.model_create_multi
    def create(self, values_list):
        new_values_list = []

        for values in values_list:
            author_partner_id = values.get('author_id', False)
            model = values.get('model', False)
            user = self.get_author_user(author_partner_id)
            company = user.company_id if user else self.env.company
            internal_user = user and user.has_group('base.group_user')
            message_type = values.get('message_type', '')
            rules = self.env['mail.replace.rule'].search([
                ('model', '=', model),
                ('company_id', '=', company.id),
                ('only_for_internal_users', '=', internal_user),
                ('message_type_filter', '=', message_type)
            ])

            final_email_from = None
            final_reply_to = None
            email_from_set = False
            reply_to_set = False

            for rule in rules:
                if rule.message_type_filter and rule.message_type_filter != values.get('message_type', ''):
                    continue

                apply_rule = not rule.domain_filter

                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, list):
                            _logger.warning("Domain filter must be a valid Odoo domain list.")
                            continue

                        if 'res_id' in values and values.get('model'):
                            related_record = self.env[values.get('model')].browse(values.get('res_id'))
                            if related_record and related_record.exists():
                                record_values = related_record.read()[0]

                                for condition in filter_condition:
                                    if isinstance(condition, (list, tuple)) and len(condition) >= 2:
                                        field_name = condition[0]
                                        if isinstance(record_values.get(field_name), tuple):
                                            record_values[field_name] = record_values[field_name][0]

                                _logger.info(f"Checking record ID {related_record.id} with values: {record_values} against domain filter {filter_condition}")

                                def evaluate_conditions(conditions, record):
                                    stack = []
                                    last_operator = None
                                    for condition in conditions:
                                        if condition == '|':
                                            last_operator = 'or'
                                        elif condition == '&':
                                            last_operator = 'and'
                                        elif isinstance(condition, (list, tuple)) and len(condition) >= 2:
                                            field, operator, value = condition
                                            field_value = record.get(field)

                                            _logger.info(f"Evaluating condition: {field} {operator} {value} (Record value: {field_value})")

                                            condition_matched = False
                                            if operator == 'not in':
                                                condition_matched = field_value not in value
                                            elif operator == 'in':
                                                condition_matched = field_value in value
                                            elif operator == '=':
                                                condition_matched = field_value == value
                                            elif operator in ('!=', '<>'):
                                                condition_matched = field_value != value

                                            if last_operator == 'or':
                                                stack[-1] = stack[-1] or condition_matched
                                            elif last_operator == 'and':
                                                stack[-1] = stack[-1] and condition_matched
                                            else:
                                                stack.append(condition_matched)

                                            last_operator = None

                                    return all(stack) if stack else True

                                if not evaluate_conditions(filter_condition, record_values):
                                    _logger.info(f"Domain filter {filter_condition} did not match. Skipping update.")
                                    apply_rule = False
                                else:
                                    _logger.info("Condition PASSED. Applying update.")
                                    apply_rule = True
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        continue

                if apply_rule and rule:
                    if rule.email_from_computed and not email_from_set:
                        final_email_from = rule.email_from_computed
                        email_from_set = True
                    if rule.reply_to_computed and not reply_to_set:
                        final_reply_to = rule.reply_to_computed
                        reply_to_set = True

                    if rule.min_attachment_size:
                        attachment_ids = []
                        for command in values.get('attachment_ids', []):
                            if isinstance(command, (list, tuple)) and len(command) >= 3 and isinstance(command[2], list):
                                attachment_ids.extend(command[2])
                            elif isinstance(command, (list, tuple)) and command[0] == 4 and isinstance(command[1], int):
                                attachment_ids.append(command[1])

                        valid_attachments = []
                        for attachment in self.env['ir.attachment'].browse(attachment_ids):
                            if attachment.file_size >= rule.min_attachment_size:
                                valid_attachments.append(attachment.id)
                            else:
                                _logger.info(f"Attachment {attachment.name} removed due to size {attachment.file_size} < {rule.min_attachment_size}")

                        values['attachment_ids'] = [(6, 0, valid_attachments)]

            if final_email_from:
                values['email_from'] = final_email_from
            if final_reply_to:
                values['reply_to'] = final_reply_to

            new_values_list.append(values)

        return super(MailMessage, self).create(new_values_list)