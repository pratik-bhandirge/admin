# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):

    _inherit = "product.product"

    is_website_publish = fields.Boolean(
        string="To show on website", default=True)

    @api.onchange('is_website_publish')
    def _onchange_is_website_publish(self):
        ''' Onchange method to check for product variant <= 1
            If the product variant is only 1, then raise message to
            unpublish product instead of hiding the product on website
        '''
        if not self.is_website_publish:
            product_variant_search_ids = self.search(
                [('product_tmpl_id', '=', self.product_tmpl_id.id)])
            if product_variant_search_ids and len(product_variant_search_ids) <= 1:
                warning_mess = {
                    'title': _('Hide Product on Website Shop!'),
                    'message': _('You can unpublish the product variant instead of hiding it. There is only one variant for this product ! '),
                }
                return {'warning': warning_mess}
