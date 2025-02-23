{
    'name': 'Product Turnover',
    'version': '1.0',
    'summary': 'Calculates product turnover based on past sales with prediction',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['sale', 'stock'],
    'external_dependencies': {'python': ['numpy']},
    'data': [
        'views/product_template_view.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
}