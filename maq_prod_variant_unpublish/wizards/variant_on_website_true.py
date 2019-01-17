# -*- coding: utf-8 -*-
from odoo import models, fields, api


class VariantTrue(models.TransientModel):

    _name = 'variant.website.true'

    @api.multi
    def change_variant_true(self):
        '''
        Method to change Product Variant visibility on website to True
        '''
        select_product_ids = self._context.get(
            'active_model') == 'product.product' and self._context.get('active_ids') or []
        product_variant_id = self.env['product.product']
        for product in select_product_ids:
            product_id = product_variant_id.browse(product)
            product_id.is_website_publish = True
