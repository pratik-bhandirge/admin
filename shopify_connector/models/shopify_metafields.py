# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ShopifyMetafields(models.Model):

    _name = 'shopify.metafields'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _rec_name = 'key'

    key = fields.Char("Key", help="Enter Key", track_visibility="onchange")
    value = fields.Char("Value", help="Enter Value",
                        track_visibility="onchange")
    value_type = fields.Char(
        "Value Type", help="Enter Value Type", track_visibility="onchange")
    namespace = fields.Char(
        "Namespace", help="Enter Value Type", track_visibility="onchange")
