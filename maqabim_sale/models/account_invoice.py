# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    ordered_qty = fields.Float(string="Ordered Qty", compute="_compute_ordered_qty", digits=dp.get_precision('Product Unit of Measure'))

    @api.multi
    @api.depends('sale_line_ids')
    def _compute_ordered_qty(self):
        for invoice_line in self.filtered(lambda l: l.sale_line_ids):
            invoice_line.ordered_qty = sum([l.product_uom_qty for l in invoice_line.sale_line_ids])
