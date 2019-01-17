# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductProduct(models.Model):

    _inherit = "product.product"

    is_website_publish = fields.Boolean(
        string="To show on website", default=True)
