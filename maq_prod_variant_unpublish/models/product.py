# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):

    _inherit = "product.product"
    is_website_publish = fields.Boolean(
        string="To show on website", default=True)
#         partners = self.env.user.partner_id
#         active_id = self._context.get('active_id')
#         if self._context.get('active_model') == 'res.partner' and active_id:
#             if active_id not in partners.ids:
#                 partners |= self.env['res.partner'].browse(active_id)
#         return partners

    website_ids = fields.Many2many("website", string="To Show on Website", 
                                   help="IF blank, the product variant will be visible in all websites")

    @api.multi
    def is_product_variant_publish(self):
        for rec in self:
            if rec.website_published:
                current_website = rec.env['website'].get_current_website()
                if not rec.website_ids and rec.is_website_publish:
                    return True
                elif not rec.is_website_publish:
                    return False
                elif rec.website_ids and rec.is_website_publish:
                    if current_website.id in rec.website_ids.ids:
                        return True
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
