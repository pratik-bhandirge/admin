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
        'stock'
    ],
    'data': [
        'views/delivery_slip_report_view_inherit.xml',
    ],
    'installable': True,
    'application': True,
}
