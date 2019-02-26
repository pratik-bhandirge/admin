# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    pos_ids = fields.Many2many('pos.config', string='Allowed Pos')
    warehouse_ids = fields.Many2many('stock.warehouse', string='Allowed Warehouses', domain="[('company_id', '=', company_id)]")
