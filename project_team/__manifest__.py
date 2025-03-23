# See LICENSE file for full copyright and licensing details.

{
    'name': 'Project - Set Team and members',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'maintainer': 'Serpent Consulting Services Pvt. Ltd.',
    'summary': 'Project Team Management',
    'category': 'Project Management',
    'website': 'https://www.serpentcs.com',
    'version': '17.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'helpdesk',
        'project',
        'crm',
    ],
    'data': [
        'views/helpdesk_team_views.xml',
        'views/project_team_views.xml',
        'views/project_team_view.xml',
    ],
    'images': [
        'static/description/ProjectTeam.png',
    ],
    'installable': True,
}
