# coding: utf-8
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    website_id = fields.Many2one('website', help='The website this sale order was created through.')


class SaleCouponApplyCode(models.TransientModel):
    _inherit = 'sale.coupon.apply.code'

    def apply_coupon(self, order, coupon_code):
        # pre-validate if coupon_code belongs to current company
        # because function is run with sudo() through
        # website_sale_coupon
        company_id = order.company_id
        program = self.env['sale.coupon.program'].search([('promo_code', '=', coupon_code),
                                                          ('company_id', '=', company_id.id)])
        coupon = self.env['sale.coupon'].search([('code', '=', coupon_code),
                                                 ('program_id.company_id', '=', company_id.id)], limit=1)

        if not program and not coupon:
            return {'not_found': _('The code %s is invalid') % (coupon_code)}
        else:
            return super(SaleCouponApplyCode, self).apply_coupon(order, coupon_code)
