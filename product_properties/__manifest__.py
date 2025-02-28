{
    'name': 'Product Properties Form',
    'version': '1.0',
    'category': 'Product',
    'summary': 'Adds technical properties form to products',
    'author': 'Custom Developer',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_property_views.xml',
    ],
    'installable': True,
    'application': False,
}