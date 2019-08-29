# -*- coding: utf-8 -*-

import random
from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_accessories(self):
        for order in self:
            current_website_id = self.env['website'].get_current_website()
            website_company_id = current_website_id.company_id
            accessory_products = []
            for products in order.website_order_line.mapped('product_id'):
                for product in products:
                    accessory_products += product.accessory_product_ids.ids
        accessory_products = self.env['product.product'].browse(accessory_products).filtered(lambda product : product.company_id == website_company_id and product.website_published)
        accessory_products -= order.website_order_line.mapped('product_id')
        return random.sample(accessory_products, len(accessory_products))