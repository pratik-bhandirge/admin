# -*- coding: utf-8 -*-

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ShopifyOdooConnector(http.Controller):

    @http.route('/shopify/<string:config_name>/order', type='json', auth="none", methods=['POST'], csrf=False)
    def shopify_order(self, config_name):
        _logger.info(
            "************Webhook call for %s config************", config_name)
#         _logger.info("************Webhook Data *************************%s",request.jsonrequest)
        if request.jsonrequest:
            shopify_order_id = request.jsonrequest.get('id')
            if config_name and shopify_order_id:
                shopify_config_rec = request.env['shopify.config'].sudo().search(
                    [('name', '=', config_name)], limit=1)
                if shopify_config_rec:
                    shopify_config_rec.check_connection()
                    shopify_config_rec.import_order(shopify_order_id)
        _logger.info("************Webhook Call End************")
        return True
