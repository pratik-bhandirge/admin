# -*- coding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)
_order_list = []


class ShopifyOdooConnector(http.Controller):

    @http.route('/shopify/<string:config_name>/order', type='json', auth="none", methods=['POST'], csrf=False)
    def shopify_order(self, config_name):
        _logger.info(
            "************Webhook call for %s config************", config_name)
        if request.jsonrequest:
            shopify_order_id = request.jsonrequest.get('id')
            if shopify_order_id in _order_list:
                _logger.info(
                    "############Webhook Call End for %s config************", config_name)
                return True
            else:
                _order_list.append(shopify_order_id)
            try:
                shopify_financial_status = request.jsonrequest.get(
                    'financial_status')
                shopify_fulfillment_status = request.jsonrequest.get(
                    'fulfillment_status')
                if config_name and shopify_order_id:
                    shopify_config_rec = request.env['shopify.config'].sudo().search(
                        [('name', '=', config_name)], limit=1)
                    allow_import = False
                    if shopify_financial_status == 'paid' and shopify_fulfillment_status == 'fulfilled':
                        allow_import = True
                    elif shopify_financial_status == 'partially_refunded' and shopify_fulfillment_status == 'partial':
                        allow_import = True
                    if allow_import:
                        shopify_config_rec.test_connection()
                        order_company = shopify_config_rec.get_shopify_order_company(
                            shopify_order_id)
                        shopify_config_rec.sudo(order_company.shopify_user_id.id).import_order(
                            shopify_order_id, order_company, allow_import)
            except:
                pass
            if shopify_order_id in _order_list:
                _order_list.remove(shopify_order_id)
        _logger.info(
            "************Webhook Call End for %s config************", config_name)
        return True
