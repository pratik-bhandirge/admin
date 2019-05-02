odoo.define('maq_website_sale.add_to_cart_b', function (require) {
'use strict';

var ajax = require('web.ajax');
require('web.dom_ready');
var weContext = require("web_editor.context");
require('website_sale.website_sale');

    $('.oe_website_sale #add_to_cart_b')
    .off('click')
    .removeClass('b-submit')
    .click(function (event) {
        event.preventDefault();

        var $form = $(this).closest('form');

        var qty_input = $form.find('input.quantity');

        var data = [];

        for(var i=0; i < qty_input.length; i++){
            console.log(qty_input[i]);
            if(qty_input[i].value != 0){
                data.push({
                    'product_id' : qty_input[i].name,
                    'quantity' : qty_input[i].value
                });
            }
        }

        $.each(data, function(i, val){
            var quantity = parseFloat(val['quantity']);
            var product_id = parseInt(val['product_id'], 10);
            $form.ajaxSubmit({
                url:  '/shop/cart/update_option',
                data: {lang: weContext.get().lang, product_id: product_id, add_qty:quantity},
                success: function (quantity) {
                    var $q = $(".my_cart_quantity");
                    $q.parent().parent().removeClass("hidden", !quantity);
                    $q.html(quantity).hide().fadeIn(600);

                }
            });
        });
		
		$form[0].reset();

    });

});
