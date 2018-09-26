# -*- coding: utf-8 -*-
{
    'name': "Ecommerce Category",

    'summary': "Adding a rule to allow/disallow categories of products by website",

    'description': "Adding a rule to allow/disallow categories of products by website",

    'author': "Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.2',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'website_multi'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/website_views.xml'
    ],
}