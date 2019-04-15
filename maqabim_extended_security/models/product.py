# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import AccessError


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def create(self, vals):
        if self.env.user.has_group('maqabim_extended_security.group_restrict_product_creation'):
            raise AccessError(_("You are not allowed to create this object."))
        return super(Product, self).create(vals)
