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
        res = [rec for rec in res if product_variant.browse(
            rec[0]).is_website_publish]
        return res
