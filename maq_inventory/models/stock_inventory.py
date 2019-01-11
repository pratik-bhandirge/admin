# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class Inventory(models.Model):

    _inherit = 'stock.inventory'

    m_supplier_ids = fields.Many2many('res.partner', string='Suppliers')
    m_internal_reference = fields.Char(string='Internal Reference')
    m_website_category_ids = fields.Many2many(
        'product.public.category', string='Website Category')

    @api.model
    def _selection_filter(self):
        """
        Add Custom Selection Options for supplier of product, internal reference, 
        and website catefory of product
        """
        result = super(Inventory, self)._selection_filter()
        result.append(('suppliers', _('Select suppliers')))
        result.append(('reference', _('Product Reference')))
        result.append(('web_categ', _('Website Product Category')))
        return result

    def _get_inventory_lines_values(self):
        """
        Inherit inventory lines method to add inventory line values according to supplier,
        internal reference and website category of the product
        """
        vals = []
        product_obj = self.env['product.product']
        quant_products = self.env['product.product']
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        args = (tuple(locations.ids),)
        domain = "location_id in %s " % args

        product_supplierinfo_obj = self.env['product.supplierinfo']
        if self.filter in ('suppliers'):
            product_supplier_ids = product_supplierinfo_obj.search([
                ('name', 'in', self.m_supplier_ids.ids),
            ])
            supplier_ids = []
            for supplier in product_supplier_ids:
                start_date = False
                end_date = False
                if supplier.date_start:
                    start_date = datetime.strptime(
                        supplier.date_start, DEFAULT_SERVER_DATE_FORMAT).date()
                if supplier.date_end:
                    end_date = datetime.strptime(
                        supplier.date_end, DEFAULT_SERVER_DATE_FORMAT).date()
                if start_date and end_date:
                    if (start_date <= datetime.today().date() <= end_date):
                        supplier_ids.append(supplier.id)
                else:
                    supplier_ids.append(supplier.id)
            product_ids = product_obj.search(
                [('seller_ids', 'in', supplier_ids)])
            if len(product_ids.ids) > 1:
                domain += " AND product_id in %s " % (tuple(product_ids.ids),)
            elif len(product_ids.ids) == 1:
                domain += " AND product_id = %s " % product_ids.ids[0]
            qry = """
                SELECT product_id, sum(quantity) as product_qty, location_id
                FROM stock_quant
                WHERE %s
                GROUP BY product_id, location_id""" % (domain)
            self.env.cr.execute(qry)

            for product_data in self.env.cr.dictfetchall():
                for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                    product_data[void_field] = False
                product_data['theoretical_qty'] = product_data['product_qty']
                if product_data['product_id']:
                    product_data['product_uom_id'] = product_obj.browse(
                        product_data['product_id']).uom_id.id
                    quant_products |= product_obj.browse(
                        product_data['product_id'])
                vals.append(product_data)
            if self.exhausted:
                for product in product_ids:
                    product_obj |= product
                exhausted_vals = self._get_exhausted_inventory_line(
                    product_obj, quant_products)
                vals.extend(exhausted_vals)
            return vals
        elif self.filter in ("web_categ"):
            product_website_categ_id = self.env['product.public.category'].search([
                ('id', 'in', self.m_website_category_ids.ids),
            ])
            product_ids = product_obj.search(
                [('public_categ_ids', 'in', product_website_categ_id.ids)])
            if product_ids:
                if len(product_ids.ids) == 1:
                    domain += " AND product_id = %s " % (product_ids.id)
                else:
                    domain += " AND product_id in %s " % (
                        tuple(product_ids.ids),)

                self.env.cr.execute(
                    """SELECT product_id, sum(quantity) as product_qty, location_id
                        FROM stock_quant
                        WHERE %s
                        GROUP BY product_id, location_id""" % (domain))
                for product_data in self.env.cr.dictfetchall():
                    for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                        product_data[void_field] = False
                    product_data['theoretical_qty'] = product_data[
                        'product_qty']
                    if product_data['product_id']:
                        product_data['product_uom_id'] = product_obj.browse(
                            product_data['product_id']).uom_id.id
                        quant_products |= product_obj.browse(
                            product_data['product_id'])
                    vals.append(product_data)
                if self.exhausted:
                    for product in product_ids:
                        product_obj |= product
                    exhausted_vals = self._get_exhausted_inventory_line(
                        product_obj, quant_products)
                    vals.extend(exhausted_vals)
                return vals
            else:
                raise ValidationError(
                    _("Product with the entered category is not available!"))
        elif self.filter in ("reference"):
            product_reference_id = self.env['product.product'].search([
                ('default_code', 'ilike', self.m_internal_reference),
            ])
            product_tuple = ()
            if product_reference_id:
                for reference in product_reference_id:
                    product_tuple = product_tuple + (reference.id,)
                if len(product_tuple) > 1:
                    domain += " AND product_id in %s " % (product_tuple,)
                elif len(product_tuple) == 1:
                    domain += " AND product_id = %s " % product_tuple
                self.env.cr.execute(
                    """SELECT product_id, sum(quantity) as product_qty, location_id
                        FROM stock_quant
                        WHERE %s
                        GROUP BY product_id, location_id""" % (domain))
                for product_data in self.env.cr.dictfetchall():
                    for void_field in [item[0] for item in product_data.items() if item[1] is None]:
                        product_data[void_field] = False
                    product_data['theoretical_qty'] = product_data[
                        'product_qty']
                    if product_data['product_id']:
                        product_data['product_uom_id'] = product_obj.browse(
                            product_data['product_id']).uom_id.id
                        quant_products |= product_obj.browse(
                            product_data['product_id'])
                    vals.append(product_data)
                if self.exhausted:
                    for product in product_reference_id:
                        product_obj |= product
                    exhausted_vals = self._get_exhausted_inventory_line(
                        product_obj, quant_products)
                    vals.extend(exhausted_vals)
                return vals
            else:
                raise ValidationError(_('There is no product available whose Internal Reference is "%s"!') % (
                    self.m_internal_reference))
        return super(Inventory, self)._get_inventory_lines_values()
