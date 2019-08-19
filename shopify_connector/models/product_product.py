# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = "product.product"

    shopify_product_product_ids = fields.One2many(
        "shopify.product.product", "product_variant_id", "Shopify Product Variants", help="Enter Shopify Product Variants")
    # shopify_weight = fields.Float(
    #     "Weight", help="Enter Shopify Product Variants", track_visibility="onchange")
    # shopify_uom = fields.Many2one(
    #     "product.uom", "Shopify UOM", help="Enter Shopify UOM", domain=[('is_shopify_uom','=',True)], track_visibility="onchange")

    @api.multi
    def check_default_code_uniq(self):
        for rec in self:
            search_product_count = self.search_count([('default_code','=',rec.default_code)])
            if search_product_count > 0:
                return False

    _constraints = [
        (check_default_code_uniq, 'Default Code must be unique per Product!',['default_code']),
    ]
