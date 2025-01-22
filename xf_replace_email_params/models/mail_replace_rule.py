
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MailReplaceRule(models.Model):
    _name = 'mail.replace.rule'
    _description = 'Mail Replace Rule'
    _order = 'sequence'

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
    domain_filter = fields.Char(
        string='Domain Filter',
        help="Optional domain filter to apply rule only for specific records. Use a domain string, e.g., [('field_name', '=', value)].",
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
        help="""
        If enabled, this rule will only apply to internal users.
        """
    )
    email_from = fields.Char(
        string='Email From',
        required=True,
    )
    reply_to = fields.Char(
        string='Reply-To',
    )

    @api.model
    def get_email_from_reply_to(self, model, company, internal_user, record_id=None):
        rules = self.search([
            ('model', '=', model),
            ('company_id', '=', company.id if company else False),
            '|', ('only_for_internal_users', '=', False), ('only_for_internal_users', '=', internal_user),
        ], order='sequence')

        for rule in rules:
            if rule.domain_filter:
                domain = eval(rule.domain_filter)
                if record_id and not self.env[model].browse(record_id).filtered_domain(domain):
                    continue

            return rule.email_from, rule.reply_to

        return None, None
