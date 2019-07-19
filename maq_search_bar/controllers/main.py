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
            category_ids = category_obj.search(
                ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
                 ('name', 'ilike', search_keyword)], limit=8)
            if len(category_ids) < 8:
                if search_keyword:
                    for srch in search_keyword.split(" "):
                        domain = ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
                                  ('name', 'ilike', srch)]
                        search_category_ids = category_obj.search(domain, limit=8)
                        category_ids += search_category_ids
                        if len(category_ids) >= 8:
                            break

            domain = super(WebsiteSaleCustom, self)._get_search_domain(search_keyword, False, False)
            product_count = prod_obj.search_count(domain)
            product_ids = prod_obj.search(domain, limit=8)
            # for srch in search_keyword.split(" "):
            #     domain = [
            #         '|', ('name', 'ilike', srch),
            #         ('product_variant_ids.default_code', 'ilike', srch),
            #         ('website_published', '=', True),
            #         # ('website_discontinued','=',False),
            #     ]
            #     product_ids = prod_obj.search(domain, limit=8)
            #     product_count = prod_obj.search_count(domain)
            # if len(product_ids) < 8:
            #     if search_keyword:
            #         for srch in search_keyword.split(" "):
            #             domain = [
            #                 '|', ('name', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
            #             search_product_ids = prod_obj.search(domain, limit=8)
            #             product_ids += search_product_ids
            #             if len(product_ids) >= 8:
            #                 break
            # domain = self._get_search_domain(search_keyword, None, [])
            # product_count = prod_obj.search_count(domain)
            # if product_count > 8:
            #     product_ids = product_ids[0:8]
            # category_ids = category_obj.search(
            #     ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
            #      ('name', 'ilike', search_keyword)], limit=8)

            # if len(category_ids) < 8:
            #     if search_keyword:
            #         for srch in search_keyword.split(" "):
            #             domain = ['|', ('website_id', '=', current_website.id), ('website_id', 'in', [False, '']),
            #                       ('name', 'ilike', srch)]
            #             search_category_ids = category_obj.search(domain, limit=8)
            #             category_ids += search_category_ids
            #             if len(category_ids) >= 8:
            #                 break
            return request.env['ir.ui.view'].render_template(
                'maq_search_bar.website_search_result', {
                    'product_ids': product_ids,
                    'product_count': product_count,
                    'search_keyword': search_keyword,
                    'category_ids': category_ids,
                })
        else:
            return False

    # def _get_search_domain(self, search, category, attrib_values):
    #     search = super(WebsiteSale, self)._get_search_domain(search, category, attrib_values)
    #     domain = request.website.sale_product_domain()
    #     if search:
    #         for srch in search.split(" "):
    #             domain += [
    #                 '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
    #                 ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]
    #
    #     if category:
    #         domain += [('public_categ_ids', 'child_of', int(category))]
    #
    #     if attrib_values:
    #         attrib = None
    #         ids = []
    #         for value in attrib_values:
    #             if not attrib:
    #                 attrib = value[0]
    #                 ids.append(value[1])
    #             elif value[0] == attrib:
    #                 ids.append(value[1])
    #             else:
    #                 domain += [('attribute_line_ids.value_ids', 'in', ids)]
    #                 attrib = value[0]
    #                 ids = [value[1]]
    #         if attrib:
    #             domain += [('attribute_line_ids.value_ids', 'in', ids)]
    #
    #     return domain
