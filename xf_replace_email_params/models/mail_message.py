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
                apply_rule = True  # ✅ Oprava: Inicializace apply_rule na True vždy na začátku pravidla
                if rule.message_type_filter and rule.message_type_filter != values.get('message_type', ''):
                    continue

                apply_rule = not rule.domain_filter

                if rule.domain_filter:
                    domain = rule.parse_domain_filter(rule.domain_filter or '[]')
                    filtered_records = self.search(domain)
                    if values.get('res_id') and values.get('model'):
                        related_record = self.env[values['model']].browse(values['res_id'])
                        if related_record in filtered_records:
                            email_from, reply_to = self.env['mail.replace.rule'].get_email_from_reply_to(model, company, internal_user)
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})

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

                            if rule.block_sending:
                                _logger.info(f"Blocking email sending for message with values: {values}")
                                self.env['mail.mail'].search([('mail_message_id', '=', values.get('id'))]).sudo().write({'state': 'cancel'})

        return super(MailMessage, self).create(values_list)
