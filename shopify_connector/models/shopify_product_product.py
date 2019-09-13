# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ShopifyProductProduct(models.Model):

    _name = 'shopify.product.product'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'product_variant_id'

#     @api.onchange("product_template_id")
#     def _set_prod_variants(self):
#         for rec in self:
#             product_template = rec.product_template_id.id
#             res = {'domain': {'product_variant_id':[('product_tmpl_id.id','=',product_template)]}}
#             return res
    @api.depends("product_variant_id")
    def _set_prod_template(self):
        for rec in self:
            if rec.product_variant_id:
                rec.product_template_id = rec.product_variant_id.product_tmpl_id.id
            else:
                rec.product_template_id = ""

    shopify_product_template_id = fields.Many2one('shopify.product.template', "Shopify Product Template",
                                                  help="Select Shopify Product Template", track_visibility='onchange', readonly=True)
    shopify_product_id = fields.Char(
        "Shopify Product Variant", help="Enter Shopify Product Variant", track_visibility='onchange', readonly=True)
    shopify_config_id = fields.Many2one("shopify.config", "Shopify Config",
                                        help="Enter Shopify Config.", track_visibility='onchange', required=True)
    shopify_inventory_item_id = fields.Char(
        "Shopify Inventory Item", help="Enter Shopify Inventory Item", track_visibility='onchange', readonly=True)
    shopify_published_variant = fields.Boolean(
        "Shopify Published Variant", default=True, help="Check if Shopify Published Variant or not?", track_visibility='onchange', readonly=True)
    product_template_id = fields.Many2one(
        "product.template", "Product Template", help="Enter Product Template", compute="_set_prod_template", track_visibility='onchange', store=True)
    product_variant_id = fields.Many2one(
        "product.product", "Product Variant", help="Enter Product Variant", track_visibility='onchange', required=True, store=True)
    default_code = fields.Char(
        "Default Code", help="Enter Default Code", related="product_variant_id.default_code", readonly="1", track_visibility='onchange')
    lst_price = fields.Float(
        string='Sale Price', help="Sale price for Shopify", required=True)
    shopify_weight = fields.Float(string="Weight", help="Weight of Product Variants",
                                  related="product_variant_id.weight", readonly=True)
    shopify_uom = fields.Many2one("product.uom", string="UOM", help="UOM of product",
                                  related="product_variant_id.uom_id", readonly=True)
    meta_fields_id = fields.Many2one("shopify.metafields", "Shopify Variant Metafields",
                                     help="Enter Shopify Variant Metafields", track_visibility='onchange')

    @api.multi
    def export_shopify_variant(self):
        for rec in self:
            shopify_config_rec = rec.shopify_config_id
            shopify_config_rec.export_prod_variant(rec)

    @api.model
    def create(self, vals):
        res = super(ShopifyProductProduct, self).create(vals)
        product_variant_id = vals.get('product_variant_id')
        shopify_config_id = vals.get('shopify_config_id')
        shopify_product_variants_count = self.env['shopify.product.product'].search_count(
            [('product_variant_id', '=', product_variant_id), ('shopify_config_id', '=', shopify_config_id)])
        shopify_product_variants = self.env['shopify.product.product'].search(
            [('product_variant_id', '=', product_variant_id), ('shopify_config_id', '=', shopify_config_id)])
        if shopify_product_variants_count > 1:
            raise ValidationError(
                _("You cannot create multiple records for same shopify configuration"))
        return res

    @api.multi
    def write(self, vals):
        res = super(ShopifyProductProduct, self).write(vals)
        for rec in self:
            product_variant_id = rec.product_variant_id.id
            shopify_config_id = vals.get('shopify_config_id')
            shopify_product_variants_count = self.env['shopify.product.product'].search_count(
                [('product_variant_id', '=', product_variant_id), ('shopify_config_id', '=', shopify_config_id)])
            shopify_product_variants = self.env['shopify.product.product'].search(
                [('product_variant_id', '=', product_variant_id), ('shopify_config_id', '=', shopify_config_id)])
            if shopify_product_variants_count > 1:
                raise ValidationError(
                    _("You cannot create multiple records for same shopify configuration"))
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.shopify_product_id:
                raise ValidationError(
                    _("You cannot delete an already exported shopify product variant!"))
        return super(AccountInvoiceLine, self).unlink()
