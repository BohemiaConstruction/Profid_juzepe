# See LICENSE file for full copyright and licensing details.

{
    'name': 'Project - Set Team and members',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'summary': 'Project Team Management',
    'category': 'Project Management',
    'website': 'https://www.serpentcs.com',
    'version': '17.0.1.0.1',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'crm',
        'helpdesk',
        'contacts',
    ],
    'data': [
        'views/project_team_view.xml',
        'views/helpdesk_team_view.xml',
        'views/partner_team_view.xml',
    ],
    'images': [
        'static/description/ProjectTeam.png',
    ],
    'installable': True,
}
