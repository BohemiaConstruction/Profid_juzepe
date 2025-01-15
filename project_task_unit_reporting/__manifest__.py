{
    "name": "Project Task Unit Reporting",
    "version": "17.0.1.0.0",
    "summary": "Allows reporting units in project task timesheets and calculates total units for tasks.",
    "category": "Project",
    "author": "Your Name",
    "license": "LGPL-3",
    "depends": ["project", "hr_timesheet", "sale"],
    "data": [
        "views/project_task_views.xml",
        "views/account_analytic_line_views.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "assets": {}
}
