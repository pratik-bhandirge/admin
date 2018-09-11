# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Maqabim Distributors: Purchase customizations",
    'summary': "Purchase customizations",
    'description': """
Maqabim Distributors: Purchase customizations
=============================================
This module will added new report on PO for priting product label
""",
    "author": "Odoo Inc",
    'website': "https://www.odoo.com",
    'category': 'Custom Development',
    'version': '0.1',
    'depends': ['purchase'],
    'data': [
        'reports/purchase_templates.xml',
        'reports/purchase_reports.xml',

        'views/purchase_views.xml'
    ],
    'license': 'OEEL-1',
}
