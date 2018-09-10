odoo.define('maqabim.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;



models.load_fields('account.tax','tax_group_id');

var _super_order = models.Order.prototype;

models.Order = models.Order.extend({

    export_for_printing: function(){
        var json = _super_order.export_for_printing.apply(this, arguments);
        json.tax_details = this.get_tax_details_by_tax_group();
        return json;
    },

    get_tax_details_by_tax_group: function(){
        var details = {};
        var fulldetails = [];
        var tax_by_group = {};

        this.orderlines.each(function(line){
            var ldetails = line.get_tax_details();
            for(var id in ldetails){
                if(ldetails.hasOwnProperty(id)){
                    details[id] = (details[id] || 0) + ldetails[id];
                }
            }
        });

        for (var id in details) {
            if(details.hasOwnProperty(id)) {
                var tax_group_id = this.pos.taxes_by_id[id].tax_group_id[0];
                var tax_group_name = this.pos.taxes_by_id[id].tax_group_id[1];
                if (tax_by_group.hasOwnProperty(tax_group_id)) {
                    tax_by_group[tax_group_id]['amount'] += details[id];
                } else {
                    tax_by_group[tax_group_id] = {
                        id: tax_group_id,
                        name: tax_group_name,
                        amount: details[id]
                    };
                }
            }
        }

        for(var id in tax_by_group){
            if(tax_by_group.hasOwnProperty(id)){
                fulldetails.push({amount: tax_by_group[id]['amount'], name: tax_by_group[id]['name']});
            }
        }
        return fulldetails;
    },
});

var _super_orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
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
