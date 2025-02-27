from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json


class MailReplaceRule(models.Model):
    _name = 'mail.replace.rule'
    _description = 'Mail Replace Rule'
    _order = 'sequence'

    name = fields.Char(
        string='Rule Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
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
    )

    domain_filter = fields.Text(
        string="Domain Filter",
        help="Filter criteria for applying the rule, e.g., [[('user_id', '=', 5)], '|', [('state', '=', 'draft'), ('priority', '>', 2)]]"
    )

    message_type_filter = fields.Selection(
        [
            ('email', 'Incoming Email'),
            ('comment', 'User Comment'),
            ('email_outgoing', 'Outgoing Email'),
            ('notification', 'System Notification'),
            ('auto_comment', 'Automated Comment'),
            ('user_notification', 'User Notification')
        ],
        string="Message Type Filter",
        default='email',
        help="Select which message type the rule applies to."
    )

    block_sending = fields.Boolean(
        string="Block Sending",
        help="If enabled, emails matching this rule will be created but not sent.",
        default=False
    )

    discard_message = fields.Boolean(
        string="Discard Message",
        help="If enabled, messages matching this rule will be discarded and not created.",
        default=False
    )

    @api.model
    def parse_domain_filter(self, domain_str):
        """ Converts a JSON string representing an Odoo domain into a valid domain list """
        try:
            domain = json.loads(domain_str)
            if isinstance(domain, list):
                return domain
        except json.JSONDecodeError:
            pass
        return []

    def apply_filter(self, records):
        """ Apply the domain filter to the given recordset """
        for rule in self:
            domain = rule.parse_domain_filter(rule.domain_filter or '[]')
            records = records.filtered_domain(domain)
        return records
