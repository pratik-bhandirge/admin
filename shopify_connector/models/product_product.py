# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit = "product.product"

    shopify_product_product_ids = fields.One2many(
        "shopify.product.product", "product_variant_id", "Shopify Product Variants", help="Enter Shopify Product Variants")
    shopify_shipping_product = fields.Boolean(
        "Is Shopify Shipping Product", help="Check if this is prduct use a shipping product while import order?", track_visibility='onchange')
    # shopify_weight = fields.Float(
    #     "Weight", help="Enter Shopify Product Variants", track_visibility="onchange")
    # shopify_uom = fields.Many2one(
    #     "product.uom", "Shopify UOM", help="Enter Shopify UOM", domain=[('is_shopify_uom','=',True)], track_visibility="onchange")

    @api.multi
    def _check_default_code_uniq_product(self):
        '''
        Prevent the default code duplication when creating product variant
        '''
        for rec in self:
            if rec.default_code:
                search_product_count = self.search_count(
                    [('default_code', '=', rec.default_code)])
                if search_product_count > 1:
                    return False
        return True

    _constraints = [
        (_check_default_code_uniq_product,
         'Default Code must be unique per Product!', ['default_code']),
    ]
