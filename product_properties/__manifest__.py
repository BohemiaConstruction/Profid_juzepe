{
    'name': 'Product Properties Fixed',
    'version': '1.1',
    'category': 'Product',
    'summary': 'Adds technical properties tab to products',
    'author': 'Custom Developer',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_property_views.xml',
    ],
    'installable': True,
    'application': False,
}