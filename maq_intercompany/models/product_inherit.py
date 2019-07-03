# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):

    _inherit = 'product.product'

#     price_extra = fields.Float(
#         'Variant Price Extra', compute='_compute_product_price_extra',
#         digits=dp.get_precision('Product Price'),
#         company_dependent=True,
#         help="This is the sum of the extra price of all attributes")

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

# class ProductAttributevalue(models.Model):
#
#     _inherit = "product.attribute.value"
#
#     price_extra = fields.Float(
#         'Attribute Price Extra', compute='_compute_price_extra', inverse='_set_price_extra',
#         default=0.0, digits=dp.get_precision('Product Price'),
#         company_dependent=True,
#         help="Price Extra: Extra price for the variant with this attribute value on sale price. eg. 200 price extra, 1000 + 200 = 1200.")
# #
# class ProductAttributePrice(models.Model):
#     _inherit = "product.attribute.price"
#
#     price_extra = fields.Float('Price Extra', company_dependent=True, digits=dp.get_precision('Product Price'))


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    '''Added fields with company dependent attribute to make them used as
       multi-company'''

    sale_ok = fields.Boolean(
        'Can be Sold', default=True, company_dependent=True,
        help="Specify if the product can be selected in a sales order line.")
    purchase_ok = fields.Boolean('Can be Purchased',
                                company_dependent=True, default=True)
#     type = fields.Selection(selection_add=[('product', 'Stockable Product')], company_dependent=True)
#     available_in_pos = fields.Boolean(string='Available in Point of Sale', company_dependent=True, help='Check if you want this product to appear in the Point of Sale', default=True)
#     m_available_pos = fields.Boolean(string="POS Available", compute="_get_pos_toggle")
    purchase_method = fields.Selection([
        ('purchase', 'On ordered quantities'),
        ('receive', 'On received quantities'),
        ], string="Control Policy", company_dependent=True,
        help="On ordered quantities: control bills based on ordered quantities.\n"
        "On received quantities: control bills based on received quantity.", default="receive")
#    list_price = fields.Float(
#        'Sales Price', default=1.0,
#        digits=dp.get_precision('Product Price'),
#        company_dependent=True,
#        help="Base price to compute the customer price. Sometimes called the catalog price.")
    description = fields.Text(
        'Description', translate=True, company_dependent=True,
        help="A precise description of the Product, used only for internal information purposes.")
    description_purchase = fields.Text(
        'Purchase Description', translate=True, company_dependent=True,
        help="A description of the Product that you want to communicate to your vendors. "
             "This description will be copied to every Purchase Order, Receipt and Vendor Bill/Credit Note.")
    description_sale = fields.Text(
        'Sale Description', translate=True, company_dependent=True,
        help="A description of the Product that you want to communicate to your customers. "
             "This description will be copied to every Sales Order, Delivery Order and Customer Invoice/Credit Note")
    description_picking = fields.Text('Description on Picking', company_dependent=True, translate=True)
    description_pickingout = fields.Text('Description on Delivery Orders', company_dependent=True, translate=True)
    description_pickingin = fields.Text('Description on Receptions', company_dependent=True, translate=True)
#     website_description = fields.Html('Description for the website', company_dependent=True, sanitize_attributes=False, translate=html_translate)
    produce_delay = fields.Float(
        'Manufacturing Lead Time', default=0.0, company_dependent=True,
        help="Average delay in days to produce this product. In the case of multi-level BOM, the manufacturing lead times of the components will be added.")
    sale_delay = fields.Float(
        'Customer Lead Time', default=0, company_dependent=True,
        help="The average delay in days between the confirmation of the customer order and the delivery of the finished products. It's the time you promise to your customers.")
#     public_categ_ids = fields.Many2many('product.public.category', string='Website Product Category', company_dependent=True,
#                                         help="Categories can be published on the Shop page (online catalog grid) to help "
#                                         "customers find all the items within a category. To publish them, go to the Shop page, "
#                                         "hit Customize and turn *Product Categories* on. A product can belong to several categories.")
#     alternative_product_ids = fields.Many2many('product.template', 'product_alternative_rel', 'src_id', 'dest_id', company_dependent=True,
#                                                string='Alternative Products', help='Suggest more expensive alternatives to '
#                                                'your customers (upsell strategy). Those products show up on the product page.')
#     accessory_product_ids = fields.Many2many('product.product', 'product_accessory_rel', 'src_id', 'dest_id', company_dependent=True,
#                                              string='Accessory Products', help='Accessories show up when the customer reviews the '
#                                              'cart before paying (cross-sell strategy, e.g. for computers: mouse, keyboard, etc.). '
#                                              'An algorithm figures out a list of accessories based on all the products added to cart.')
#     optional_product_ids = fields.Many2many('product.template', 'product_optional_rel', 'src_id', 'dest_id', company_dependent=True,
#                                             string='Optional Products', help="Optional Products are suggested "
#                                             "whenever the customer hits *Add to Cart* (cross-sell strategy, "
#                                             "e.g. for computers: warranty, software, etc.).")
    inventory_availability = fields.Selection([
        ('never', 'Sell regardless of inventory'),
        ('always', 'Show inventory on website and prevent sales if not enough stock'),
        ('threshold', 'Show inventory below a threshold and prevent sales if not enough stock'),
        ('custom', 'Show product-specific notifications'),
    ], string='Inventory Availability', company_dependent=True, help='Adds an inventory availability status on the web product page.', default='never')
#     website_style_ids = fields.Many2many('product.style', company_dependent=True, string='Styles')
    invoice_policy = fields.Selection(
        [('order', 'Ordered quantities'),
         ('delivery', 'Delivered quantities'),
        ], string='Invoicing Policy', company_dependent=True,
        help='Ordered Quantity: Invoice based on the quantity the customer ordered.\n'
             'Delivered Quantity: Invoiced based on the quantity the vendor delivered (time or deliveries).',
        default='order')


#     def action_view_stock_move_lines(self):
#         '''This method inherits the default odoo method and updates the domain
#            for the stock move lines related to the product company wise'''
#         res = super(ProductTemplate, self).action_view_stock_move_lines()
#         res.update({'domain': ['&',
#                                ('product_id.product_tmpl_id', 'in', self.ids),
#                                '|', '|', ('location_id.company_id.id', 'in',
#                                           self.env.user.company_ids.ids),
#                                ('location_id.company_id.id', '=', None),
#                                '|', ('location_dest_id.company_id.id', 'in',
#                                      self.env.user.company_ids.ids),
#                                ('location_dest_id.company_id.id', '=', None)]})
#         return res
#     @api.depends('available_in_pos')
#     def _get_pos_toggle(self):
#         for rec in self:
#             current_company = rec.env['res.users']._get_company()
#             if rec.available_in_pos and current_company:
#                 rec.m_available_pos = True
#             elif not rec.available_in_pos:
#                 rec.m_available_pos = False

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
