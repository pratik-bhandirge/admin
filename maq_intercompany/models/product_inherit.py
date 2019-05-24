# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductProduct(models.Model):

    _inherit ='product.product'

    def action_view_stock_move_lines(self):
        res = super(ProductProduct, self).action_view_stock_move_lines()
        res.update({'domain': ['&',('product_id', '=', self.id),
                               '|','|',
                               ('location_id.company_id','=',
                                self.env.user.company_id.id),
                               ('location_id.company_id.id','=',None),
                               '|',('location_dest_id.company_id','=',
                                    self.env.user.company_id.id),
                               ('location_dest_id.company_id.id','=',None)]})
        return res


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    def action_view_stock_move_lines(self):
        res = super(ProductTemplate, self).action_view_stock_move_lines()
        res.update({'domain': ['&',
                               ('product_id.product_tmpl_id', 'in', self.ids),
                               '|','|',('location_id.company_id','=',
                                        self.env.user.company_id.id),
                               ('location_id.company_id.id','=',None),
                               '|',('location_dest_id.company_id','=',
                                    self.env.user.company_id.id),
                               ('location_dest_id.company_id.id','=',None)]})
        return res


    def action_view_routes(self):
        routes = self.mapped('route_ids') | \
            self.mapped('categ_id').mapped('total_route_ids') | \
            self.env['stock.location.route'].\
                search([('warehouse_selectable', '=', True)])
        res = super(ProductTemplate, self).action_view_routes()
        res.update({'domain': ['&',
                               ('id', 'in', routes.ids),'|',
                               ('company_id','=',self.env.user.company_id.id),
                               ('company_id','=',None)]})
        return res