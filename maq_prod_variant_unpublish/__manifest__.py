# -*- coding: utf-8 -*-

{
    'name': 'Product Variant Show/Hide',
    'version': '1.0',
    'summary': 'Show or Hide Product Variant on the website shop',
    'description': "",
    'depends': ['product', 'sale', 'website_sale'],
    'category': 'Sale',
    'data': [
        'views/product_view.xml',
        'wizards/variant_on_website_false_view.xml',
        'wizards/variant_on_website_true_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
