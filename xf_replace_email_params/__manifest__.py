# -*- coding: utf-8 -*-

{
    'name': 'Replace email_from and reply_to',
    'version': '1.1.6',
    'category': 'Productivity,Discuss,Extra Tools',
    'summary': """
    Replace "Email From" and "Reply To" parameters in emails
    """,
    'author': 'Systee s.r.o. (https://www.systee.cz)',
    'description': """
    This module helps to replace/overwrite email_from and reply_to parameters of outgoing emails and notifications.
    After module installation you can customize email from and reply to options.
    """,
    'license': 'Other proprietary',
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/mail_replace_rule.xml',
    ],
    'images': [
        'static/description/xf_replace_email_params.png',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'qweb': [],
}
