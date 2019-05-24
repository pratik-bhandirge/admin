# coding: utf-8

from datetime import datetime, timedelta, time

from odoo import fields, http, _
from odoo.addons.website_sale.controllers.backend import WebsiteSaleBackend
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class WebsiteMultiBackend(WebsiteSaleBackend):

    # add website_id arg
    # this whole function is overriden because it needs to take into account website_id
    @http.route()
    def fetch_dashboard_data(self, date_from, date_to, website_id):
        results = super(WebsiteSaleBackend, self).fetch_dashboard_data(date_from, date_to)
        current_website = request.env['website'].browse(website_id) if website_id else request.env['website'].get_current_website()

        sales_values = dict(
            graph=[],
            best_sellers=[],
            summary=dict(
                order_count=0, order_carts_count=0, order_unpaid_count=0,
                order_to_invoice_count=0, order_carts_abandoned_count=0,
                payment_to_capture_count=0, total_sold=0,
                order_per_day_ratio=0, order_sold_ratio=0, order_convertion_pctg=0,
            )
        )
        results['dashboards']['sales'] = sales_values

        results['groups']['sale_salesman'] = request.env['res.users'].has_group('sales_team.group_sale_salesman')
        if not results['groups']['sale_salesman']:
            return results

        date_date_from = fields.Date.from_string(date_from)
        date_date_to = fields.Date.from_string(date_to)
        date_diff_days = (date_date_to - date_date_from).days
        datetime_from = datetime.combine(date_date_from, time.min)
        datetime_to = datetime.combine(date_date_to, time.max)

        date_from = date_date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to = date_date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # Product-based computation
        report_product_lines = request.env['sale.report'].read_group(
            domain=[
                ('product_id.website_published', '=', True),
                ('website_id', '=', current_website.id),
                ('state', 'in', ['sale', 'done']),
                ('date', '>=', date_from),
                ('date', '<=', date_to)],
            fields=['product_id', 'product_uom_qty', 'price_subtotal'],
            groupby='product_id', orderby='product_uom_qty desc', limit=5)
        for product_line in report_product_lines:
            product_id = request.env['product.product'].browse(product_line['product_id'][0])
            sales_values['best_sellers'].append({
                'id': product_id.id,
                'name': product_id.name,
                'qty': product_line['product_uom_qty'],
                'sales': product_line['price_subtotal'],
            })

        # Sale-based results computation
        sale_order_domain = [
            ('website_id', '=', current_website.id),
            ('date_order', '>=', fields.Datetime.to_string(datetime_from)),
            ('date_order', '<=', fields.Datetime.to_string(datetime_to))]
        so_group_data = request.env['sale.order'].read_group(sale_order_domain, fields=['state'], groupby='state')
        for res in so_group_data:
            if res.get('state') == 'sent':
                sales_values['summary']['order_unpaid_count'] += res['state_count']
            elif res.get('state') in ['sale', 'done']:
                sales_values['summary']['order_count'] += res['state_count']
            sales_values['summary']['order_carts_count'] += res['state_count']

        report_price_lines = request.env['sale.report'].read_group(
            domain=[
                ('website_id', '=', current_website.id),
                ('state', 'in', ['sale', 'done']),
                ('date', '>=', date_from),
                ('date', '<=', date_to)],
            fields=['team_id', 'price_subtotal'],
            groupby=['team_id'],
        )
        sales_values['summary'].update(
            order_to_invoice_count=request.env['sale.order'].search_count(sale_order_domain + [
                ('state', 'in', ['sale', 'done']),
                ('order_line', '!=', False),
                ('partner_id', '!=', request.env.ref('base.public_partner').id),
                ('invoice_status', '=', 'to invoice'),
            ]),
            order_carts_abandoned_count=request.env['sale.order'].search_count(sale_order_domain + [
                ('is_abandoned_cart', '=', True),
                ('cart_recovery_email_sent', '=', False)
            ]),
            payment_to_capture_count=request.env['payment.transaction'].search_count([
                ('state', '=', 'authorized'),
                # that part perform a search on sale.order in order to comply with access rights as tx do not have any
                ('sale_order_id.id', 'in', request.env['sale.order'].search(sale_order_domain + [('state', '!=', 'cancel')]).ids),
            ]),
            total_sold=sum(price_line['price_subtotal'] for price_line in report_price_lines)
        )

        # Ratio computation
        sales_values['summary']['order_per_day_ratio'] = round(float(sales_values['summary']['order_count']) / date_diff_days, 2)
        sales_values['summary']['order_sold_ratio'] = round(float(sales_values['summary']['total_sold']) / sales_values['summary']['order_count'], 2) if sales_values['summary']['order_count'] else 0
        sales_values['summary']['order_convertion_pctg'] = 100.0 * sales_values['summary']['order_count'] / sales_values['summary']['order_carts_count'] if sales_values['summary']['order_carts_count'] else 0

        # Graphes computation
        if date_diff_days == 7:
            previous_sale_label = _('Previous Week')
        elif date_diff_days > 7 and date_diff_days <= 31:
            previous_sale_label = _('Previous Month')
        else:
            previous_sale_label = _('Previous Year')

        sales_domain = [
            ('website_id', '=', current_website.id),
            ('state', 'in', ['sale', 'done']),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
        ]
        sales_values['graph'] += [{
            'values': self._compute_sale_graph(date_date_from, date_date_to, sales_domain),
            'key': 'Untaxed Total',
        }, {
            'values': self._compute_sale_graph(date_date_from - timedelta(days=date_diff_days), date_date_from, sales_domain, previous=True),
            'key': previous_sale_label,
        }]

        results['websites'] = request.env['website'].search_read([], ['id', 'name'])
        for website in results['websites']:
            if website['id'] == current_website.id:
                website['selected'] = True

        return results
