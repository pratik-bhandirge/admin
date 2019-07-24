# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/search_result'], type='json', auth="public", website=True)
    def search_result(self, search_keyword=None):
        prod_obj = request.env['product.template']
        category_obj = request.env['product.public.category']
        current_website = request.env['website'].get_current_website()
        if search_keyword:
            category_ids = category_obj.sudo().search(
                ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
                 ('name', 'ilike', search_keyword)], limit=8)
            if len(category_ids) < 8:
                if search_keyword:
                    for srch in search_keyword.split(" "):
                        domain = ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
                                  ('name', 'ilike', srch)]
                        search_category_ids = category_obj.sudo().search(domain, limit=8)
                        category_ids += search_category_ids
                        if len(category_ids) >= 8:
                            category_ids = category_ids[0:8]
                            break
            domain = []
            for srch in search_keyword.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
            product_ids = prod_obj.sudo().search(domain, limit=8)
            product_count = len(product_ids)
            return request.env['ir.ui.view'].render_template(
                'maq_search_bar.website_search_result', {
                    'product_ids': product_ids,
                    'product_count': product_count,
                    'search_keyword': search_keyword,
                    'category_ids': category_ids,
                })
        else:
            return False
