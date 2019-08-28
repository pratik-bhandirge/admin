# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    shopify_product_template_ids = fields.One2many("shopify.product.template", 'product_tmpl_id',
                                                   "Shopify Product Templates", help="Select Shopify Product Templates", track_visibility='onchange')
    prod_tags_ids = fields.Many2many("shopify.prod.tags", 'shopify_prod_tags_template_rel', 'prod_tag_id', 'product_template_id',
                                     "Prod. Tags", help="Enter Prod. Tags", track_visibility='onchange', domain=[('is_province', '=', False)])
    province_tags_ids = fields.Many2many("shopify.prod.tags", 'shopify_province_tags_template_rel', 'province_tag_id', 'product_template_id',
                                         "Province Tags", help="Enter Province Tags", track_visibility='onchange', domain=[('is_province', '=', True)])
    allowed_variants_ids = fields.One2many("shopify.product.product", "product_template_id",
                                           "Allowed Variants", help="Enter Allowed Variants", track_visibility='onchange', domain=lambda self: [('product_template_id', 'in', self.ids)])
#     prod_tmpl_id = fields.Many2one("product.template", "Product Template ID",
#                                    help="Enter Product Template ID", track_visibility='onchange')
    published_on_shopify = fields.Boolean(
        "Published on Shopify", help="Published on Shopify", track_visibility='onchange')

    @api.multi
    def _check_default_code_uniq_template(self):
        for rec in self:
            if rec.default_code:
                search_product_count = self.search_count(
                    [('default_code', '=', rec.default_code)])
                if search_product_count > 1:
                    return False
        return True

    _constraints = [
        (_check_default_code_uniq_template,
         'Default Code must be unique per Product!', ['default_code']),
    ]
