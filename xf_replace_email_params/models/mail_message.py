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
                            raise ValueError("Domain filter must be a valid dictionary, e.g., {'support_team': 1}")
                        
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
                            email_from, reply_to = self.env['mail.replace.rule'].get_email_from_reply_to(model, company, internal_user)
                            if email_from:
                                values.update({'email_from': email_from})
                            if reply_to is not None:
                                values.update({'reply_to': reply_to})
                    except Exception as e:
                        _logger.error(f"Error applying filter: {e}")
                        raise ValueError(f"Invalid filter condition: {e}")
                
                # Filtrace podle velikosti příloh
                if rule.min_attachment_size:
                    attachment_ids = []
                    for command in values.get('attachment_ids', []):
                        if isinstance(command, (list, tuple)) and len(command) >= 3:
                            attachment_ids.extend(command[2])  # Extrahujeme ID příloh
                        elif isinstance(command, (list, tuple)) and command[0] == 4:
                            attachment_ids.append(command[1])  # Přidání jednotlivých příloh
                    
                    valid_attachments = []
                    for attachment in self.env['ir.attachment'].browse(attachment_ids):
                        if attachment.file_size >= rule.min_attachment_size:
                            valid_attachments.append(attachment.id)
                        else:
                            _logger.info(f"Attachment {attachment.name} removed due to size {attachment.file_size} < {rule.min_attachment_size}")
                    
                    values['attachment_ids'] = [(6, 0, valid_attachments)]
                
                # Pokud bylo pravidlo aplikováno, neaplikujeme další pravidla
                break
        
        return super(MailMessage, self).create(values_list)