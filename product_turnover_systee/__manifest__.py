{
    'name': 'Product Turnover',
    'version': '1.0',
    'summary': 'Calculates product turnover based on past sales',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['sale', 'stock'],
    'data': [
        'views/product_template_view.xml',
        'data/ir_cron_data.xml',
    ],
    'installable': True,
    'application': False,
}