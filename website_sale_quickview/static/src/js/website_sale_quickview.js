odoo.define('website_sale_quickview.website_sale_quickview', function(require) {
"use strict";

require('web.dom_ready');
require('website_sale.website_sale');
var base = require("web_editor.base");
var ajax = require('web.ajax');
var utils = require('web.utils');
var core = require('web.core');
var _t = core._t;

function price_to_str(price) {
    var l10n = _t.database.parameters;
    var precision = 2;

    if ($(".decimal_precision").length) {
        precision = parseInt($(".decimal_precision").last().data('precision'));
    }
    var formatted = _.str.sprintf('%.' + precision + 'f', price).split('.');
    formatted[0] = utils.insert_thousand_seps(formatted[0]);
    return formatted.join(l10n.decimal_point);
}

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

$('.oe_website_sale .btn-quickview')
    .off('click')
    // .removeClass('a-submit')
    .click(function (event) {
        event.preventDefault();
        ajax.jsonRpc("/products/quickview", 'call', {
                'product_id': parseInt($(this).data('product_id')),
            }).then(function (modal) {
                var $modal = $(modal);

                $modal.modal().show()

                $modal.on('hidden.bs.modal', function () {
                    $(this).hide();
                    $(this).siblings().filter(".modal-backdrop").remove(); // bootstrap leaves a modal-backdrop
                    $(this).remove();
                });

                $modal.on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
                    var $ul = $(ev.target).closest('.js_add_cart_variants');
                    var $parent = $ul.closest('.js_product');
                    var $product_id = $parent.find('.product_id').first();
                    var $price = $parent.find(".oe_price:first .oe_currency_value");
                    var $default_price = $parent.find(".oe_default_price:first .oe_currency_value");
                    var $optional_price = $parent.find(".oe_optional:first .oe_currency_value");
                    var variant_ids = $ul.data("attribute_value_ids");
                    if(_.isString(variant_ids)) {
                        variant_ids = JSON.parse(variant_ids.replace(/'/g, '"'));
                    }
                    var values = [];
                    var unchanged_values = $parent.find('div.oe_unchanged_value_ids').data('unchanged_value_ids') || [];

                    $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function () {
                        values.push(+$(this).val());
                    });
                    values =  values.concat(unchanged_values);

                    $parent.find("label").removeClass("text-muted css_not_available");

                    var product_id = false;
                    for (var k in variant_ids) {
                        if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                            $.when(base.ready()).then(function() {
                                $price.html(price_to_str(variant_ids[k][2]));
                                $default_price.html(price_to_str(variant_ids[k][3]));
                            });
                            if (variant_ids[k][3]-variant_ids[k][2]>0.01) {
                                $default_price.closest('.oe_website_sale').addClass("discount");
                                $optional_price.closest('.oe_optional').show().css('text-decoration', 'line-through');
                                $default_price.parent().removeClass('hidden');
                            } else {
                                $optional_price.closest('.oe_optional').hide();
                                $default_price.parent().addClass('hidden');
                            }
                            product_id = variant_ids[k][0];
                            update_product_image(this, product_id);
                            break;
                        }
                    }

                    $parent.find("input.js_variant_change:radio, select.js_variant_change").each(function () {
                        var $input = $(this);
                        var id = +$input.val();
                        var values = [id];

                        $parent.find("ul:not(:has(input.js_variant_change[value='" + id + "'])) input.js_variant_change:checked, select.js_variant_change").each(function () {
                            values.push(+$(this).val());
                        });

                        for (var k in variant_ids) {
                            if (!_.difference(values, variant_ids[k][1]).length) {
                                return;
                            }
                        }
                        $input.closest("label").addClass("css_not_available");
                        $input.find("option[value='" + id + "']").addClass("css_not_available");
                    });

                    if (product_id) {
                        $parent.removeClass("css_not_available");
                        $product_id.val(product_id);
                        $parent.find("#add_to_cart").removeClass("disabled");
                    } else {
                        $parent.addClass("css_not_available");
                        $product_id.val(0);
                        $parent.find("#add_to_cart").addClass("disabled");
                    }
                });

                $modal.on('click', 'a.js_add_cart_json', function (ev) {
                    ev.preventDefault();
                    var $link = $(ev.currentTarget);
                    var $input = $link.parent().find("input");
                    var product_id = +$input.closest('*:has(input[name="product_id"])').find('input[name="product_id"]').val();
                    var min = parseFloat($input.data("min") || 0);
                    var max = parseFloat($input.data("max") || Infinity);
                    var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val() || 0, 10);
                    var new_qty = quantity > min ? (quantity < max ? quantity : max) : min;
                    // if they are more of one input for this product (eg: option modal)
                    $('input[name="'+$input.attr("name")+'"]').add($input).filter(function () {
                        var $prod = $(this).closest('*:has(input[name="product_id"])');
                        return !$prod.length || +$prod.find('input[name="product_id"]').val() === product_id;
                    }).val(new_qty).change();
                    return false;
                });

                $modal.on('click', '.a-submit', function (ev) {
                    event.preventDefault();
                    $(this).closest('form').submit();
                });
            });
        return false;
    });
});
