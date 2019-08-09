# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def action_view_stock_move_lines(self):
        res = super(ProductProduct, self).action_view_stock_move_lines()
        res.update({'domain': ['&', ('product_id', '=', self.id),
                               '|', '|',
                               ('location_id.company_id', '=',
                                self.env.user.company_ids.ids),
                               ('location_id.company_id.id', '=', None),
                               '|', ('location_dest_id.company_id', '=',
                                     self.env.user.company_ids.ids),
                               ('location_dest_id.company_id.id', '=', None)]})
        return res

class ProductAttributePrice(models.Model):
    _inherit = "product.attribute.price"

    @api.depends('product_tmpl_id','value_id')
    def _get_product_variant(self):
        for rec in self:
            product_tmpl_id = rec.product_tmpl_id
            value_id = rec.value_id
            if product_tmpl_id and value_id:
                product_variants = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_tmpl_id.id),('attribute_value_ids','=',value_id.id)], limit=1)
                if product_variants:
                    rec.product_id = product_variants.id
                else:
                    rec.product_id = False
            else:
                rec.product_id = False
    price_extra = fields.Float('Price Extra', company_dependent=True, digits=dp.get_precision('Product Price'))
    product_id = fields.Many2one('product.product', 'Product', compute='_get_product_variant')


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    '''Added fields with company dependent attribute to make them used as
       multi-company'''

    sale_ok = fields.Boolean(
        'Can be Sold', default=True, company_dependent=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased',
                                company_dependent=True, default=True)
    available_in_pos = fields.Boolean(string='Available in Point of Sale', company_dependent=True,
        help='Check if you want this product to appear in the Point of Sale', default=True)
    purchase_method = fields.Selection([
        ('purchase', 'On ordered quantities'),
        ('receive', 'On received quantities'),
        ], string="Control Policy", company_dependent=True,
        help="On ordered quantities: control bills based on ordered quantities.\n"
        "On received quantities: control bills based on received quantity.", default="receive")
    list_price = fields.Float(
        'Sales Price', default=1.0,
        digits=dp.get_precision('Product Price'),
        company_dependent=True,
        help="Base price to compute the customer price. Sometimes called the catalog price.")
    produce_delay = fields.Float(
        'Manufacturing Lead Time', default=0.0, company_dependent=True,
        help="Average delay in days to produce this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added.")
    sale_delay = fields.Float(
        'Customer Lead Time', default=0, company_dependent=True,
        help="The average delay in days between the confirmation of the customer order and the delivery of the finished products. It's the time you promise to your customers.")
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities'),
        ], string='Invoicing Policy', company_dependent=True,
        help='Ordered Quantity: Invoice based on the quantity the customer ordered.\n'
             'Delivered Quantity: Invoiced based on the quantity the vendor delivered (time or deliveries).',
        default='order')
    inventory_availability = fields.Selection([
        ('never', 'Sell regardless of inventory'),
        ('always', 'Show inventory on website and prevent sales if not enough stock'),
        ('threshold', 'Show inventory below a threshold and prevent sales if not enough stock'),
        ('custom', 'Show product-specific notifications'),
    ], string='Inventory Availability', company_dependent=True, help='Adds an inventory availability status on the web product page.', default='never')
    available_threshold = fields.Float(string='Availability Threshold', company_dependent=True, default=5.0)
    custom_message = fields.Text(string='Custom Message', company_dependent=True, default='')

    def action_view_routes(self):
        '''This method inherits the default odoo method and updates the domain
           for the routes related to the product company wise'''
        routes = self.mapped('route_ids') | \
            self.mapped('categ_id').mapped('total_route_ids') | \
            self.env['stock.location.route'].\
            search([('warehouse_selectable', '=', True)])
        res = super(ProductTemplate, self).action_view_routes()
        res.update({'domain': ['&',
                               ('id', 'in', routes.ids), '|',
                               ('company_id.id', 'in', self.env.user.company_ids.ids),
                               ('company_id', '=', None)]})
        return res


class ProductStyle(models.Model):
    _inherit = "product.style"

    company_id = fields.Many2one('res.company', string="Company")
