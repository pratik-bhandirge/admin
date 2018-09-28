# -*- coding: utf-8 -*-
{
    'name': "Website Style Edits",

    'summary': "Editing the styling on some elements on the Maqabim wesbite",

    'description': "Editing the styling on some elements on the Maqabim wesbite",

    'author': "Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['portal'],

    # always loaded
    'data': [
        'views/templates.xml',
    ],
}