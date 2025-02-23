{
    'name': 'Product Turnover Systee',
    'version': '1.0',
    'depends': ['base', 'web', 'sale'],
    'data': [
        'views/product_template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_turnover_systee/static/lib/chart.bundle.min.js',
            'product_turnover_systee/static/src/js/product_turnover.js',
        ],
    },
    'installable': True,
    'application': False,
}
