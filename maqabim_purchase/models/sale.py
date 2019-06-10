# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_uom_qty)

    @api.model
    def create(self, vals):
        if vals.get('product_uom_qty') and 'print_qty' not in vals:
            vals['print_qty'] = int(vals['product_uom_qty'])
        res = super(SaleOrderLine, self).create(vals)
        return res
