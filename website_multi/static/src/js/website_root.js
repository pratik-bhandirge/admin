odoo.define('website_multi.WebsiteRoot', function (require) {
    'use strict';
    var ajax = require('web.ajax');
    var WebsiteRoot = require('website.WebsiteRoot').WebsiteRoot;

    WebsiteRoot.include({
        events: _.extend({}, WebsiteRoot.prototype.events || {}, {
            'click .js_multi_website_switch': '_multiWebsiteSwitch',
        }),

        _multiWebsiteSwitch: function (event) {
            var id_to_switch_to = event.target.id.substring('multi_website_'.length);
            return ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model:  'ir.config_parameter',
                method: 'set_param',
                args: ['website_multi.force_website_id', id_to_switch_to],
                kwargs: {},
            }).then(function () {
                window.location.reload(true);
            });
        },
    });
});
