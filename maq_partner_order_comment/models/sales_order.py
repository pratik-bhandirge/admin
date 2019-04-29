
from odoo import models, fields

class SaleOrder(models.Model):

    _inherit = 'sale.order'

    partner_comment = fields.Text("Partner Order Comment")

