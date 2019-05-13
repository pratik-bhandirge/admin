# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.onchange("is_website_publish")
    def onchange_is_website_publish(self):
        if self.is_website_publish == False:
            self.website_ids = None

    @api.onchange("is_hide_variant")
    def onchange_is_website_publish(self):
        if self.is_hide_variant == False:
            self.product_hide_website_ids = None


    is_website_publish = fields.Boolean(
        string="To Show 'Currently Out of Stock' message", default=False)
    is_hide_variant = fields.Boolean(
        string='To Hide Product Variant', default=False)
#         partners = self.env.user.partner_id
#         active_id = self._context.get('active_id')
#         if self._context.get('active_model') == 'res.partner' and active_id:
#             if active_id not in partners.ids:
#                 partners |= self.env['res.partner'].browse(active_id)
#         return partners

    website_ids = fields.Many2many("website", relation="product_product_website_rel",
                                   string="Websites",
                                   help="IF blank, the product variant will be visible in all websites")

    product_hide_website_ids = fields.Many2many("website",
                                                relation="product_product_hide_website_rel",
                                                string="Hide Product from Websites")


    @api.multi
    def is_product_variant_publish(self):
        for rec in self:
            if rec.website_published:
                current_website = rec.env['website'].get_current_website()
                if not rec.website_ids and rec.is_website_publish:
                    return False
                elif not rec.is_website_publish and not rec.website_ids:
                    return True
                elif rec.website_ids and rec.is_website_publish:
                    if current_website.id in rec.website_ids.ids:
                        return False
                    else:
                        return True
            else:
                return False


    @api.multi
    def is_product_variant_hide(self):
        for rec in self:
            if rec.website_published:
                current_website = rec.env['website'].get_current_website()
                if not rec.product_hide_website_ids and rec.is_hide_variant:
                    return True
                elif not rec.product_hide_website_ids and not rec.is_hide_variant:
                    return False
                elif rec.product_hide_website_ids and rec.is_hide_variant:
                    if current_website in rec.product_hide_website_ids:
                        return True
                    else:
                        return False
            else:
                return False


#     @api.onchange('is_website_publish')
#     def _onchange_is_website_publish(self):
#         ''' Onchange method to check for product variant <= 1
#             If the product variant is only 1, then raise message to
#             unpublish product instead of hiding the product on website
#         '''
#         if not self.is_website_publish:
#             product_variant_search_ids = self.search(
#                 [('product_tmpl_id', '=', self.product_tmpl_id.id)])
#             if product_variant_search_ids and len(product_variant_search_ids) <= 1:
#                 warning_mess = {
#                     'title': _('Hide Product on Website Shop!'),
#                     'message': _('You can unpublish the product variant instead of hiding it. There is only one variant for this product ! '),
#                 }
#                 return {'warning': warning_mess}
