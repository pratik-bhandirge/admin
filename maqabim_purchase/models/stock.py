# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    print_qty = fields.Integer(string="Print Qty")

    @api.onchange('product_uom_qty')
    def onchange_quantity(self):
        self.print_qty = int(self.product_uom_qty)


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, values, group_id)
        if values.get('print_qty', 0):
            result['print_qty'] = values['print_qty']
        return result
