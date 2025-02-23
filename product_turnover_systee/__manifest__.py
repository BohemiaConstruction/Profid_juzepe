{
    'name': 'Product Turnover',
    'version': '1.0',
    'summary': 'Calculates product turnover based on past sales with visualization',
    'category': 'Sales',
    'author': 'Your Name',
    'depends': ['sale', 'stock', 'web'],
    'external_dependencies': {'python': []},
    'data': [
        'views/product_template_view.xml',
    ],
    'installable': True,
    'application': False,
}