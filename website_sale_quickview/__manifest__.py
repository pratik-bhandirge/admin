# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Website Products Quick View (eCommerce)',
    'version' : '1.1',
    'summary': 'Shows product details on popup window',
    'sequence': 30,
    'description': """
        This module adds option to show product 
        details on popup window in website.
    """,
    'category': 'eCommerce',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['website_sale'],
    'data': [
        'views/assets_registry.xml',
        'views/templates.xml',
    ],
    'demo': [

    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'price': 30.0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: