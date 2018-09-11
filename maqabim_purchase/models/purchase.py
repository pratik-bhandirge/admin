# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_qty)
