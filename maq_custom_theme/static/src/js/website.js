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

    $('.oe_website_sale').on('click', 'tr.variant_details label[label-default="label-default"]', function (ev) {
        var product_id = $(ev.target).closest('tr.variant_details')[0].id;
        console.log(product_id);
        $('.oe_website_sale').find('label.active').each(function () {
            this.style.color = "#555555";
            this.className = '';
        });
        this.style.color = "#1ad68f";
        this.className = 'active';
        update_product_image(this, product_id);
    });

    function update_product_image(event_source, product_id) {
        var $img;
        if ($('#o-carousel-product').length) {
            $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img');
            $img.attr("src", "/web/image/product.product/" + product_id + "/image");
            $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                .data('oe-model', 'product.product').data('oe-id', product_id);

            var $thumbnail = $(event_source).closest('tr.js_product, .oe_website_sale').find('img.js_variant_img_small');
            if ($thumbnail.length !== 0) { // if only one, thumbnails are not displayed
                $thumbnail.attr("src", "/web/image/product.product/" + product_id + "/image/90x90");
                $('.carousel').carousel(0);
            }
        }
        else {
            $img = $(event_source).closest('tr.js_product, .oe_website_sale').find('span[data-oe-model^="product."][data-oe-type="image"] img:first, img.product_detail_img');
            $img.attr("src", "/web/image/product.product/" + product_id + "/image");
            $img.parent().attr('data-oe-model', 'product.product').attr('data-oe-id', product_id)
                .data('oe-model', 'product.product').data('oe-id', product_id);
        }
        // reset zooming constructs
        $img.filter('[data-zoom-image]').attr('data-zoom-image', $img.attr('src'));
        if ($img.data('zoomOdoo') !== undefined) {
            $img.data('zoomOdoo').isReady = false;
        }
    }

});
