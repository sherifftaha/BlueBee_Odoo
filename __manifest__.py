{
    'name': 'Invoice Deadline & Block',
    'version': '1.1',
    'summary': 'Manage invoice deadlines, grace periods, and customer blocking',
    'author': 'Bluebee',
    'depends': ['sale', 'website_sale', 'website_sale_product_configurator', 'account'],
    'data': [
        'data/cron.xml',
        'data/payment_config.xml',
        'data/below_minimum_fee_product.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'invoice_deadline/static/src/js/invoice_deadline.js',
            'invoice_deadline/static/src/js/cart_modal_patch.js',
        ],
    },
    'installable': True,
    'application': False,
}
