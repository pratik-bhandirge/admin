# -*- coding: utf-8 -*-

{
    'name': 'MAQ Inventory Adjustment',
    'version': '1.0',
    'summary': 'Extra filters added for Inventory adjustment',
    'description': """In Inventory adjustment add following filters
    1. Select suppliers
    2. Product Reference
    3. Website Product Category
    Following features will be added
    Req Id. 1.42 - Reverse Shipment information for processing
    Req Id. 1.98 - Approval process for inventory adjustment
    Req Id. 2.00 - Set the checkbox ticked by default
    """,
    'depends': ['stock', 'website_sale', 'stock_account'],
    'category': 'Warehouse',
    'data': [
        'security/ir.model.access.csv',
        'security/maq_security.xml',
        'views/stock_inventory_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
