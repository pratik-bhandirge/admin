# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    m_customer_ref = fields.Char(string="Customer Reference", track_visibility='onchange')


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    m_delivery_customer_ref = fields.Char(
        related='sale_id.m_customer_ref', string="Customer Reference", track_visibility='onchange')
