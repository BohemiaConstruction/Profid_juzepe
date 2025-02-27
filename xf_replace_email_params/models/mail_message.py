from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class MailMessage(models.Model):
    _inherit = 'mail.message'

    def get_author_user(self, author_partner_id):
        apply_rule = False  # Výchozí inicializace
        if not author_partner_id:
            return None
        partner = self.env['res.partner'].with_context(active_test=False).browse(author_partner_id)
        if partner and partner.user_ids:
            for user in partner.user_ids:
                return user

    @api.model_create_multi
    def create(self, values_list):
        apply_rule = False  # Výchozí inicializace
        new_values_list = []
        
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
                
                apply_rule = not rule.domain_filter
                
                if rule.domain_filter:
                    try:
                        filter_condition = eval(rule.domain_filter)
                        if not isinstance(filter_condition, list):
                            _logger.warning("Domain filter must be a valid Odoo domain list, e.g., [('support_team', '=', 1)]")
                            continue
                        
                        if 'res_id' in values and values.get('model'):
                            related_record = self.env[values.get('model')].browse(values.get('res_id'))
                            if related_record and related_record.exists():
                                simplified_record_values = {}
                                for condition in filter_condition:
                                    if isinstance(condition, (list, tuple)) and len(condition) >= 2:
                                        field = condition[0]
                                        if isinstance(field, str) and hasattr(related_record, field):
                                            value = getattr(related_record, field)
                                            if isinstance(value, models.BaseModel):
                                                value = value.id  # Extract Many2one ID
                                            simplified_record_values[field] = value
                                
                                _logger.info(f"Checking record ID {related_record.id} with simplified values: {simplified_record_values}")

                                # 🔹 Použijeme search_count pro přesné ověření filtru
                                if not self.env[values.get('model')].sudo().search_count([('id', '=', related_record.id)] + filter_condition):
                                    _logger.info(f"Domain filter {filter_condition} did not match. Skipping update.")
                                    continue
                                else:
                                    apply_rule = True
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        continue
                
                if apply_rule:
                    email_from, reply_to = self.env['mail.replace.rule'].get_email_from_reply_to(model, company, internal_user)
                    if email_from:
                        values.update({'email_from': email_from})
                    if reply_to is not None:
                        values.update({'reply_to': reply_to})
                    
                    # Filtrace podle velikosti příloh
                    if rule.min_attachment_size:
                        attachment_ids = []
                        for command in values.get('attachment_ids', []):
                            if isinstance(command, (list, tuple)) and len(command) >= 3 and isinstance(command[2], list):
                                attachment_ids.extend(command[2])  # Extrahujeme ID příloh
                            elif isinstance(command, (list, tuple)) and command[0] == 4 and isinstance(command[1], int):
                                attachment_ids.append(command[1])  # Přidání jednotlivých příloh

                        valid_attachments = []
                        for attachment in self.env['ir.attachment'].browse(attachment_ids):
                            if attachment.file_size >= rule.min_attachment_size:
                                valid_attachments.append(attachment.id)
                            else:
                                _logger.info(f"Attachment {attachment.name} removed due to size {attachment.file_size} < {rule.min_attachment_size}")

                        values['attachment_ids'] = [(6, 0, valid_attachments)]

                    # Blokování odeslání zprávy
                    if rule.block_sending:
                        _logger.info(f"Blocking email sending for message with values: {values}")
                        self.env['mail.mail'].search([('mail_message_id', '=', values.get('id'))]).sudo().write({'state': 'cancel'})
            
            new_values_list.append(values)
        
        return super(MailMessage, self).create(new_values_list)
