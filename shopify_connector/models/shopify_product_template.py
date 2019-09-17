# -*- coding: utf-8 -*-

import shopify

from odoo import models, fields, api, _
from odoo.tools.translate import html_translate
from odoo.exceptions import ValidationError


class ShopifyProductTemplate(models.Model):

    _name = 'shopify.product.template'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'product_tmpl_id'

    @api.multi
    @api.onchange('shopify_config_id')
    def onchange_shopify_config(self):
        '''
        Set Vendor and product type according to shopify config ID
        '''
        for rec in self:
            if rec.shopify_config_id:
                rec.vendor = ""
                rec.product_type = ""
                return {'domain': {'vendor': [('shopify_config_id', '=', rec.shopify_config_id.id)],
                                   'product_type': [('shopify_config_id', '=', rec.shopify_config_id.id)]}}

    name = fields.Char("Name", help="Enter Name", track_visibility='onchange')
    shopify_config_id = fields.Many2one("shopify.config", "Shopify Config",
                                        help="Enter Shopify Config", track_visibility='onchange', required=True)
    body_html = fields.Html("Body Html", help="Enter Body Html",
                            track_visibility='onchange', translate=html_translate)
    vendor = fields.Many2one("shopify.vendor", "Shopify Vendor",
                             help="Enter Shopify Vendor", track_visibility='onchange')
    product_type = fields.Many2one("shopify.product.type", "Shopify Product Type",
                                   help="Enter Shopify Product Type", track_visibility='onchange')
    shopify_published = fields.Boolean(
        "Shopify Published",  help="Enter Shopify Published", track_visibility='onchange', default=False, readonly=True)
    shopify_prod_tmpl_id = fields.Char(
        "Shopify Product Template ID", help="Enter Shopify Product Template ID", track_visibility='onchange', readonly=True)
    meta_fields_id = fields.Many2one("shopify.metafields", "Shopify Metafields",
                                     help="Enter Shopify Metafields", track_visibility='onchange')
    image_ids = fields.Many2many("shopify.images", 'shopify_product_template_images_rel', 'product_template_id',
                                 'image_id', "Shopify Images", help="Enter Shopify Metafields", track_visibility='onchange')
    product_tmpl_id = fields.Many2one(
        "product.template", "Product Template", help="Enter Product Template", required=True, track_visibility='onchange')
    shopify_error_log = fields.Text(
        "Shopify Error", help="Error occurs while exporting move to the shopify",
        readonly=True)

    @api.model
    def create(self, vals):
        '''
        Prevent the user to create a shopify product template record with the same shopify config.
        '''
        res = super(ShopifyProductTemplate, self).create(vals)
        product_template_id = vals.get('product_tmpl_id')
        shopify_config_id = vals.get('shopify_config_id')
        shopify_product_templates = self.env['shopify.product.template'].search_count(
            [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
        if shopify_product_templates > 1:
            raise ValidationError(
                _("You cannot create multiple records for same shopify configuration"))
        return res

    @api.multi
    def write(self, vals):
        '''
        Prevent the user to update a shopify product template record with the same shopify config.
        '''
        res = super(ShopifyProductTemplate, self).write(vals)
        for rec in self:
            product_template_id = rec.product_tmpl_id.id
            shopify_config_id = vals.get('shopify_config_id')
            shopify_product_variants_count = self.env['shopify.product.template'].search_count(
                [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
            shopify_product_variants = self.env['shopify.product.template'].search(
                [('product_tmpl_id', '=', product_template_id), ('shopify_config_id', '=', shopify_config_id)])
            if shopify_product_variants_count > 1:
                raise ValidationError(
                    _("You cannot create multiple records for same shopify configuration"))
        return res

#     @api.multi
#     def unlink(self):
#         for rec in self:
#             if rec.shopify_prod_tmpl_id:
#                 raise ValidationError(
#                     _("You cannot delete an already exported shopify product!"))
#         return super(AccountInvoiceLine, self).unlink()

    @api.multi
    def export_shopify(self):
        '''
        This method is called by export button and it checks if product or province tags are set and then,
        it calls the export product method on shopify config object.
        '''
        for rec in self:
            if not rec.shopify_prod_tmpl_id:
                shopify_config_rec = rec.shopify_config_id
                if rec.product_tmpl_id.prod_tags_ids or rec.product_tmpl_id.province_tags_ids:
                    shopify_config_rec.export_product(rec)
                elif not (rec.product_tmpl_id.prod_tags_ids or rec.product_tmpl_id.province_tags_ids):
                    raise ValidationError(
                        _("Please select atleast 1 product or province tags before exporting product to shopify!"))
#             elif rec.shopify_prod_tmpl_id:
#                 raise ValidationError(_("The product is already exported to shopify!"))

    @api.multi
    def update_shopify_product(self):
        '''
        Process shopify product template updation from odoo to shopify

        1. Check the connection of odoo with shopify.
        2. Get the respective field values like shopify product template id, product and province tags,
           product template name, body html, vendor, product type.
        3. Set all the fields values on shopify product and save the shopify product object.
        '''
        self.shopify_config_id.check_connection()
        for rec in self:
            shopify_product_id = str(rec.shopify_prod_tmpl_id)
            prod_tags = rec.product_tmpl_id.prod_tags_ids
            province_tags = rec.product_tmpl_id.province_tags_ids
            str_prod_province_tags = []
            for prod_tag in prod_tags:
                str_prod_province_tags.append(prod_tag.name)
            for prov_tag in province_tags:
                str_prod_province_tags.append(prov_tag.name)
            tags = ",".join(str_prod_province_tags)

            product_template_name = str(rec.product_tmpl_id.name)
            product_template_body_html = rec.body_html
            product_template_vendor = rec.vendor.name
            product_template_product_type = rec.product_type.name
            product_template_tags = tags
            is_shopify_product = shopify.Product.exists(shopify_product_id)
            if is_shopify_product:
                shopify_product = shopify.Product({'id': shopify_product_id,
                                                   'title': product_template_name,
                                                   'body_html': product_template_body_html,
                                                   'vendor': product_template_vendor,
                                                   'product_type': product_template_product_type,
                                                   'tags': product_template_tags})
                success = shopify_product.save()
            else:
                raise ValidationError(_("Product Template does not exist in shopify !"))

#     @api.multi
#     def website_publish_button(self):
#         self.shopify_config_id.check_connection()
#         for rec in self:
#             if not rec.shopify_published:
#                 rec.shopify_published = True
#                 shopify_product_id = str(rec.shopify_prod_tmpl_id)
#                 shopify_product = shopify.Product({'id': shopify_product_id, 'published': rec.shopify_published})
#                 success = shopify_product.save()

#     @api.multi
#     def website_unpublish_button(self):
#         self.shopify_config_id.check_connection()
#         for rec in self:
#             if rec.shopify_published:
#                 rec.shopify_published = False
#                 shopify_product_id = str(rec.shopify_prod_tmpl_id)
#                 shopify_product = shopify.Product({'id': shopify_product_id, 'published': rec.shopify_published})
#                 success = shopify_product.save()
