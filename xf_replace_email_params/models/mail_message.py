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
            message_type = values.get('message_type', False)
            user = self.get_author_user(author_partner_id)
            company = user and user.company_id
            internal_user = user and user.has_group('base.group_user')
            
            # Filtrace pravidel podle message_type a domain_filter
            rules = self.env['mail.replace.rule'].search([])
            for rule in rules:
                if rule.message_type_filter and rule.message_type_filter != message_type:
                    continue
                if rule.domain_filter:
                    domain_filter_eval = eval(rule.domain_filter)
                    if not self.env['mail.message'].search(domain_filter_eval):
                        continue
                
                email_from, reply_to = rule.get_email_from_reply_to(model, company, internal_user)
                if email_from:
                    values.update({'email_from': email_from})
                if reply_to is not None:
                    values.update({'reply_to': reply_to})
        
        return super(MailMessage, self).create(values_list)
