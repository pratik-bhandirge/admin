
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockMove(models.Model):

    '''
    Added Box number field in stock.move model
    '''
    _inherit = 'stock.move'

    m_box_number = fields.Char(string="Box Number")
