# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    shopify_name = fields.Char(
        "Shopify Name", help="Enter Shopify Name", track_visibility='onchange', readonly=True)
    shopify_order_id = fields.Char(
        "Shopify Order ID", help="Enter Shopify Order ID", track_visibility='onchange', readonly=True)
    shopify_note = fields.Char(
        "Shopify Note", help="Enter Shopify Note", track_visibility='onchange', readonly=True)
    shopify_fulfillment_status = fields.Char(
        "Shopify Fulfillment Status", help="Enter Shopify Fulfillment Status", track_visibility='onchange', readonly=True)
    shopify_financial_status = fields.Char(
        "Shopify Financial Status", help="Enter Shopify Financial Status", track_visibility='onchange', readonly=True)
    shopify_import_status = fields.Selection([('successfull_import', 'Successfully Imported'), ('fail_to_create_do', 'Failed to Create Delivery Order'), (
        'fail_to_create_invoice', 'Failed To Create Invoice'), ('other', 'Other')], "Shopify Import Status", help="Enter Shopify Import Status", track_visibility='onchange', readonly=True)
    shopify_error_message = fields.Char(
        "Shopify Error Message", help="Enter Shopify Error Message", track_visibility='onchange', readonly=True)
    shopify_config_id = fields.Many2one(
        "shopify.config", "Shopify Config", readonly=True)
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        print ("view_type --->>", view_type)
        if view_type == 'tree' and self._context.get('shopify_sale_order'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//tree"):
                if self._context['shopify_sale_order'] == 1:
                    node.set('create', "false")
                    node.set('delete','false')
                else:
                    node.set('create', "true")
                    node.set('delete','true')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        if view_type == 'form' and self._context.get('shopify_sale_order'):
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//form"):
                if self._context['shopify_sale_order'] == 1:
                    node.set('create', "false")
                    node.set('delete','false')
                else:
                    node.set('create', "true")
                    node.set('delete','true')
            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    shopify_order_line_id = fields.Char(
        "Shopify Order Line ID", help="Enter Shopify Order Line ID", track_visibility='onchange', readonly=True)
