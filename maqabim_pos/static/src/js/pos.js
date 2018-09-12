odoo.define('maqabim.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;



models.load_fields('account.tax','tax_group_id');

var _super_order = models.Order.prototype;

models.Order = models.Order.extend({

    export_for_printing: function() {
        var json = _super_order.export_for_printing.apply(this, arguments);
        json.tax_details = this.get_tax_details_by_tax_group();
        return json;
    },

    get_tax_details_by_tax_group: function() {
        var fulldetails = [];

        this.orderlines.each(function(line) {
            var ldetails = line.get_tax_details_by_group();
            for (var id in ldetails) {
                if (ldetails.hasOwnProperty(id)) {
                    var details = _.findWhere(fulldetails, {
                        id: id
                    });
                    if (details) {
                        details['amount'] += ldetails[id]['amount'];
                    } else {
                        fulldetails.push({
                            amount: ldetails[id]['amount'],
                            name: ldetails[id]['name'],
                            id: id,
                        });
                    }
                }
            }
        });
        return _.sortBy(fulldetails, 'amount');
    },
});
var _super_orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
    get_tax_details_by_group: function(){
        return this.get_all_prices().taxByGroup;
    },
    get_all_prices: function() {
        /*
            complete override to group the taxes by tax group
            changes are marked with CUSTOM
        */
        var self = this;
        var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
        var taxtotal = 0;

        var product =  this.get_product();
        var taxes_ids = product.taxes_id;
        var taxes =  this.pos.taxes;
        var taxdetail = {};
        var product_taxes = [];

        _(taxes_ids).each(function(el){
            product_taxes.push(_.detect(taxes, function(t){
                return t.id === el;
            }));
        });

        var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
        _(all_taxes.taxes).each(function(tax) {
            taxtotal += tax.amount;
            taxdetail[tax.id] = tax.amount;
        });

        //CUSTOM
        var tax_by_group = {};
        _.each(product_taxes, function(pt) {
            var pt = self._map_tax_fiscal_position(pt) || pt;
            var group_id = pt.tax_group_id[0];
            tax_by_group[group_id] = {amount: 0, name: pt.tax_group_id[1]};
            _.each(all_taxes.taxes, function(tx) {
                if(tx.id == pt.id || _.contains(_.pluck(pt.children_tax_ids, 'id'), tx.id)) {
                    tax_by_group[group_id]['amount'] += tx.amount;
                }
            });
        });

        return {
            "priceWithTax": all_taxes.total_included,
            "priceWithoutTax": all_taxes.total_excluded,
            "tax": taxtotal,
            "taxDetails": taxdetail,
            "taxByGroup": tax_by_group, //custom
        };
    },
    generate_wrapped_product_name: function() {
        /*
            complete override to append the internal reference on xml receipt, a receipt that print via posbox
            changes are marked with CUSTOM
        */
        var MAX_LENGTH = 24; // 40 * line ratio of .6
        var wrapped = [];
        //CUSTOM START
        var name = '';
        if (this.get_product().default_code)
            name += '[' + this.get_product().default_code + ']'
        name = name + this.get_product().display_name;
        //CUSTOM END
        var current_line = "";
        while (name.length > 0) {
            var space_index = name.indexOf(" ");

            if (space_index === -1) {
                space_index = name.length;
            }

            if (current_line.length + space_index > MAX_LENGTH) {
                if (current_line.length) {
                    wrapped.push(current_line);
                }
                current_line = "";
            }

            current_line += name.slice(0, space_index + 1);
            name = name.slice(space_index + 1);
        }

        if (current_line.length) {
            wrapped.push(current_line);
        }
        return wrapped;
    },
});

screens.OrderWidget.include({
    update_summary: function() {
        /*
            Override to display the subtotal and taxes by group
        */
        var order = this.pos.get_order();
        if (!order.get_orderlines().length) {
            return;
        }

        var subtotal = order ? order.get_total_without_tax() : 0;
        var total     = order ? order.get_total_with_tax() : 0;
        var taxes     = order ? total - subtotal : 0;

        var $tax_details = $(QWeb.render('TaxGroup', {widget: this}));

        this.el.querySelector('.summary .total > .value').textContent = this.format_currency(total);
        $tax_details.appendTo($(this.el.querySelector('.summary .total .subentry')).empty());
        this.el.querySelector('.summary .total .subtotal .value').textContent = this.format_currency(subtotal);
    },
});


});
