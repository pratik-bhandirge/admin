# coding: utf-8

import logging

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    website_shop_login = fields.Boolean(string='Requires Login to Shop')