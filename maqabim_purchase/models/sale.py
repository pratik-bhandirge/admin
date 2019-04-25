# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_uom_qty)

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        res['print_qty'] = self.product_uom_qty
        return res
