{
    'name': 'Nappy’s Minimart — Website & Shop',
    'version': '19.0.1.0.3',
    'summary': 'Community minimart website, live Odoo shop and red-and-gold branding',
    'category': 'Website/eCommerce',
    'author': 'Spxcorp Limited',
    'website': 'https://spxcorp.net',
    'license': 'LGPL-3',
    'depends': ['website_sale', 'point_of_sale'],
    'data': [
        'views/settings.xml', 'views/layout.xml', 'views/commerce.xml',
        'data/categories.xml', 'data/pages.xml', 'views/pos_display.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('prepend', 'nappys_website/static/src/css/brand_variables.scss'),
        ],
        'web.assets_frontend': [
            'nappys_website/static/src/css/fonts.css',
            'nappys_website/static/src/css/storefront.scss',
            'nappys_website/static/src/js/storefront.js',
        ],
        'web.assets_backend': ['nappys_website/static/src/css/backend.scss'],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'installable': True,
    'application': True,
}
