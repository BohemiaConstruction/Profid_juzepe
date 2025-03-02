{
    'name': 'Product Properties Fixed Corrected',
    'version': '1.2',
    'category': 'Product',
    'summary': 'Adds technical properties to products and removes database duplicates',
    'author': 'Custom Developer',
    'depends': ['product'],
    'data': [
        'views/product_property_views.xml',
    ],
    'installable': True,
    'application': False,
    'post_init_hook': 'hooks.cleanup_database_hook'
}