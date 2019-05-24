# coding: utf-8

from odoo import api, fields, models
from odoo.http import request


class View(models.Model):
    _inherit = 'ir.ui.view'

    def _create_website_specific_pages_for_view(self, new_view, website):
        self.ensure_one()

        for page in self.page_ids:
            new_page = page.copy_exact()
            new_page.view_id = new_view
            new_page.website_ids |= website
            page._create_website_specific_menu_items(new_page, website)

    @api.multi
    def write(self, vals):
        '''COW for ir.ui.view. This way editing websites does not
        impact other websites and so that newly created websites will
        only contain the default views.
        '''
        # todo jov: multi
        current_website_id = self._context.get('website_id')

        # if generic view in multi-website context
        for view in self:
            if current_website_id and not view.website_id and not self._context.get('no_cow') and self.env['website'].search_count([]) > 1:
                new_website_specific_view = view.copy({'website_id': current_website_id})
                view.with_context(no_cow=True)._create_website_specific_pages_for_view(new_website_specific_view, self.env['website'].browse(current_website_id))

                new_website_specific_view.write(vals)
            else:
                super(View, view).write(vals)

    # todo jov deduplicate with mixin or something like that? See e.g. _compute_most_specific_child_ids
    @api.model
    def get_related_views(self, key, bundles=False):
        '''Make this only return most specific views for website.'''
        views = super(View, self).get_related_views(key, bundles=bundles)
        current_website_id = self._context.get('website_id')
        most_specific_views = self.env['ir.ui.view']

        if not current_website_id:
            return views

        if current_website_id:
            for view in views:
                if (view.website_id and view.website_id.id == current_website_id) or\
                   (not view.website_id and not any(view.key == view2.key and view2.website_id and view2.website_id.id == current_website_id for view2 in views)):
                    most_specific_views |= view

        return most_specific_views

    @api.model
    def _prepare_qcontext(self):
        qcontext = super(View, self)._prepare_qcontext()

        if request and getattr(request, 'is_frontend', False):
            domain_based_info = {'id': 'domain_based', 'name': 'Domain Based'}
            forced_website_id = request.env['ir.config_parameter'].sudo().get_param('website_multi.force_website_id')
            if forced_website_id and forced_website_id.isdigit():
                selected_website = self.env['website'].browse(int(forced_website_id))
                qcontext['multi_website_selected_website'] = {'id': selected_website.id, 'name': selected_website.name}
            else:
                qcontext['multi_website_selected_website'] = domain_based_info

            qcontext['multi_website_websites'] = [{'id': website.id, 'name': website.name} for website in self.env['website'].search([])]
            qcontext['multi_website_websites'] += [domain_based_info]

        return qcontext
