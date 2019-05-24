odoo.define('website_multi.backend.dashboard', function (require) {
"use strict";
var WebsiteBackend = require('website.backend.dashboard');

WebsiteBackend.include({
    /* Have to add one additional parameter: website_id Not really
     * possible in a clean way I think, so override the whole
     * function.
     */
    fetch_data: function() {
        var self = this;
        return this._rpc({
            route: '/website/fetch_dashboard_data',
            params: {
                website_id: this.website_id || false,
                date_from: this.date_from.year()+'-'+(this.date_from.month()+1)+'-'+this.date_from.date(),
                date_to: this.date_to.year()+'-'+(this.date_to.month()+1)+'-'+this.date_to.date(),
            },
        }).done(function(result) {
            self.data = result;
            self.websites = result.websites;
            self.dashboards_data = result.dashboards;
            self.currency_id = result.currency_id;
            self.groups = result.groups;
        });
    },
    
    on_website_button: function(website_id) {
        var self = this;
        this.website_id = website_id;
        $.when(this.fetch_data()).then(function() {
            self.$('.o_website_dashboard_content').empty();
            self.render_dashboards();
            self.render_graphs();
        });
    },

    update_cp: function() {
        var self = this;
        this._super.apply(this, arguments);
        this.$searchview.find('button.js_website').click(function(ev) {
            self.$searchview.find('button.js_website.active').removeClass('active');
            $(ev.target).addClass('active');
            self.on_website_button($(ev.target).data('website-id'));
        });
    },
});
});
