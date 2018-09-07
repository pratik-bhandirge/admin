odoo.define('maqabim.pos', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');
var core = require('web.core');

var QWeb = core.qweb;

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


});
