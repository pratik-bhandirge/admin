# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleExt(WebsiteSale):

    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product which should be available

        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        res = super(WebsiteSaleExt, self).get_attribute_value_ids(product)
        product_variant = request.env['product.product'].sudo()
        for rec in res:
            product_variant_id = product_variant.browse(rec[0])
            if product_variant_id.is_website_publish == False:
                res.remove(rec)
        return res
