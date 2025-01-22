
from odoo import models, api


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, values_list):
        for values in values_list:
            author_partner_id = values.get('author_id', False)
            model = values.get('model', False)
            res_id = values.get('res_id', False)
            user = self.env['res.users'].search([('partner_id', '=', author_partner_id)], limit=1)
            company = user.company_id if user else self.env.company
            internal_user = user.has_group('base.group_user') if user else False

            email_from, reply_to = self.env['mail.replace.rule'].get_email_from_reply_to(
                model, company, internal_user, record_id=res_id
            )

            if email_from:
                values['email_from'] = email_from
            if reply_to:
                values['reply_to'] = reply_to

        return super(MailMessage, self).create(values_list)
