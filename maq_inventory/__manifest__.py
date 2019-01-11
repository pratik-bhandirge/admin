# -*- coding: utf-8 -*-

{
    'name': 'MAQ Inventory Adjustment',
    'version': '1.0',
    'summary': 'Extra filters added for Inventory adjustment',
    'description': """In Inventory adjustment add following filters
    1. Select suppliers
    2. Product Reference
    3. Website Product Category
    """,
    'depends': ['stock', 'website_sale'],
    'category': 'Warehouse',
    'data': [
        'views/stock_inventory_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
