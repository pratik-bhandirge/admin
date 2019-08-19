# -*- coding: utf-8 -*-

from . import models

from odoo import api, SUPERUSER_ID


# TODO: Apply proper fix & remove in master
def _create_company_records(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    for company in companies:
        company_name = str(company.name or '')
        code = "SW"
        for letter in company_name.split():
            code += letter[0]
            if len(code) == 5:
                break
        shopify_vendor_id = env['res.partner'].create({'name': 'Shopify Vendor - ' + company_name,
                                                       'supplier': True,
                                                       'customer': False})

        pricelist_rec = env['product.pricelist'].create(
            {'name': 'Shopify pricelist -' + company_name, 'discount_policy': 'with_discount', 'company_id': company.id})
        print("pricelist_rec****************************************************",pricelist_rec)
        if pricelist_rec:
            cust_vals = {'name': 'Shopify Customer - ' + company_name,
                         'property_product_priclist': pricelist_rec.id, 'supplier': False, 'customer': True}
        else:
            cust_vals = {'name': 'Shopify Customer - ' + company_name, 
                         'supplier': False, 'customer': True}
        shopify_customer_id = env['res.partner'].create(cust_vals)

        warehouse_code_search = env[
            'stock.warehouse'].search_count([('code', '=', code)])
        if warehouse_code_search > 0:
            count = 1
            while warehouse_code_search > 0:
                code = code[:-1] + \
                    str(count) if len(code) >= 5 else code + str(count)
                count = count + 1
                warehouse_code_search = env[
                    'stock.warehouse'].search_count([('code', '=', code)])
        shopify_warehouse_id = env['stock.warehouse'].create({'name': 'Shopify Warehouse - ' + company_name + '[' + code + ']',
                                                              'code': code,
                                                              'company_id': company.id})
        shopify_location_id = shopify_warehouse_id.lot_stock_id
        try:
            company.write({'shopify_vendor_id': shopify_vendor_id.id,
                           'shopify_customer_id': shopify_customer_id.id,
                           'shopify_warehouse_id': shopify_warehouse_id.id,
                           'shopify_location_id': shopify_location_id.id})
        except:
            pass
