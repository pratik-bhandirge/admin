# -*- coding: utf-8 -*-

{
    'name': 'Maq Intercompany',
    'category': 'Custom',
    'summary': 'Stock move line record action update to keep move lines discrete company wise',
    'version': '11.0.1.0.0',
    'author': 'Bista Solutions',
    'website': 'http://www.bistasolutions.com',
    'license': 'AGPL-3',
    'description': """
    Stock move line record action update to keep move lines discrete company wise
        """,
    'depends': [
        'stock','product', 'website_multi', 'website_sale', 'ecommerce_category', 'sale_coupon',
        'calendar'
    ],
    'data': [
        'security/intercompany_security.xml',
#         'views/calendar_event_view.xml',
        'views/delivery_slip_report_view_inherit.xml',
        'views/product_public_categ_view.xml',
        'views/product_template_inherit.xml',
    ],
    'installable': True,
    'application': True,
    'uninstall_hook': 'uninstall_hook',
}
