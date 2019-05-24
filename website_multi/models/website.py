# coding: utf-8

import logging

from odoo import api, fields, models, tools
from odoo.http import request
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    # these fields are configured as ir.config.parameter records in standard Odoo
    # they have been prefixed with website_ to try to avoid confusion between the two
    website_auth_signup_uninvited = fields.Selection([
        ('b2b', 'On invitation (B2B)'),
        ('b2c', 'Free sign up (B2C)'),
    ], default='b2b', string='Signup policy')
    website_template_user_id = fields.Many2one('res.users', help='Used when people sign up through the website.')

    @api.multi
    def _compute_menu(self):
        super(Website, self)._compute_menu()
        Menu = self.env['website.menu']

        # super doesn't try to find non-website specific menu items
        for website in self:
            website.menu_id = Menu.search([
                ('parent_id', '=', False),
                '|', ('website_id', '=', website.id), ('website_id', '=', False)
            ], order='id', limit=1)

    @api.multi
    def _prepare_sale_order_values(self, partner, pricelist):
        values = super(Website, self)._prepare_sale_order_values(partner, pricelist)
        values['website_id'] = self._context.get('website_id')
        return values

    @api.model
    def get_current_website(self):
        website = super(Website, self).get_current_website()

        if request:
            forced_website_id = request.env['ir.config_parameter'].sudo().get_param('website_multi.force_website_id')

            try:
                forced_website = request.env['website'].browse(int(forced_website_id))
            except ValueError:
                forced_website = False

            if forced_website:
                _logger.info('Forcing website %s (ID: %s)', forced_website.name, forced_website.id)

                # switch to appropriate public user if necessary
                if request.env.user.has_group('base.group_public'):
                    _logger.info('Switching to public user %s (ID: %s) for website %s',
                                 forced_website.user_id.login, forced_website.user_id.id,
                                 forced_website.id)
                    forced_website = forced_website.sudo(forced_website.user_id.id)

                # this was set by super
                request.context = dict(request.context, website_id=forced_website.id)

                return forced_website

        return website


class Page(models.Model):
    _inherit = 'website.page'
    _order = 'specificity'

    specificity = fields.Integer(compute='_compute_specifity', store=True,
                                 help='''Used to order pages from most specific (i.e. belonging to 1 website)
                                 to least specific (i.e. not belonging to a website.). Note that this is defined
                                 in ascending order, so a specificity of 0 is a page for 1 website (i.e. most specific).''')

    @api.multi
    @api.depends('website_ids')
    def _compute_specifity(self):
        '''This defines a specificity as follows:

        |--------------------+-------------|
        | amount of websites | specificity |
        |--------------------+-------------|
        |                  1 |           0 |
        |                  2 |           1 |
        |                ... |         ... |
        |                  0 |         MAX |
        |--------------------+-------------|

        So when there are multiple pages for a given url, the most
        specific one will be chosen.
        '''
        for page in self:
            if page.website_ids:
                page.specificity = len(page.website_ids) - 1
            else:
                # This is an arbitrary maximum, the important thing is
                # that this should always be greater than #websites - 1.
                # Presumably noone is going to create >1024 websites...
                page.specificity = 1024

    @api.multi
    def _is_most_specific_page(self, page_to_test):
        '''This will figure out if page_to_test is the most specific page in self.'''
        pages_for_url = self.filtered(lambda page: page.url == page_to_test.url)

        # this works because pages are _order'ed by specificity
        most_specific_page = pages_for_url[0]

        return most_specific_page == page_to_test

    @api.multi
    def copy_exact(self):
        '''The standard copy() of page does a bunch of things we don't
        want. This function calls copy() and then undos these things.
        '''
        exact_copies = self.env['website.page']

        for page in self:
            new_page = page.copy()

            # get rid of the newly created view. Link the new_page to
            # the new view before unlinking the view, otherwise the
            # page will be deleted by the ondelete="cascade" on
            # website.page's view_id
            view_created_by_copy = new_page.view_id
            new_page.view_id = page.view_id
            view_created_by_copy.unlink()

            # set fields that have been made unique to their original
            # value again
            new_page.name = page.name
            new_page.url = page.url

            # False by default
            new_page.website_published = True

            exact_copies |= new_page

        return exact_copies

    @api.multi
    def _create_website_specific_menu_items(self, new_page, new_website):
        for page in self:
            for menu in page.menu_ids:
                # Don't copy menu items that wouldn't be displayed for
                # this website.
                if menu.parent_id and menu in menu.parent_id.most_specific_child_ids:
                    # Don't copy menu items that are already website
                    # specific. Instead link them to the new page.
                    if menu.website_id == new_website:
                        menu.page_id = new_page
                    else:
                        menu.copy({
                            'page_id': new_page.id,
                            'website_id': new_website.id,
                        })

    @api.multi
    def _create_website_specific_pages(self, excluded_websites):
        for page in self:
            assert not page.website_ids, '{} is not a generic page, it belongs to {}'.format(page, page.website_ids)
            for website_needing_page in self.env['website'].search([]) - excluded_websites:
                page_for_website = page.copy_exact()
                page_for_website.website_ids = website_needing_page
                page_for_website.view_id.website_id = website_needing_page
                page._create_website_specific_menu_items(page_for_website, website_needing_page)

    @api.model
    def delete_page(self, page_id):
        '''Don't delete the menu items associated to a page before unlinking
        so the necessary copies can be made.'''
        page = self.env['website.page'].browse(int(page_id))
        menu_ids = page.menu_ids
        page.unlink()

        # we don't invoke cow in this case because duplicating of the
        # menu items is handled by the website.page cow.
        menu_ids.with_context(no_cow=True).unlink()

    @api.multi
    def unlink(self):
        '''When a user deletes a page on website A it should only be deleted
        from website A, not all websites. Because COW is used to copy
        pages on demand it's possible that the page the user wants to
        delete is a generic one (no website_ids). When this happens we
        create copies of this page for every other website.

        Note that for this, this is not specifically necessary,
        because website.page has a website_ids m2m. However,
        ir.ui.view does not and there are options like website_indexed
        and date_publish that need to be set per website so the m2m is
        not that useful here.
        '''
        Website = self.env['website']
        current_website_id = self._context.get('website_id')

        if current_website_id:
            for page in self:
                if Website.search_count([]) > 1 and not page.website_ids:
                    page._create_website_specific_pages(Website.browse(current_website_id))

        return super(Page, self).unlink()


class Menu(models.Model):
    _inherit = 'website.menu'

    most_specific_child_ids = fields.Many2many('website.menu', compute='_compute_most_specific_child_ids',
                                               help='''Based on child_id but instead will only get the most specific menu
                                               item for the current website.''')

    @api.multi
    @api.depends('child_id.website_id')
    def _compute_most_specific_child_ids(self):
        current_website_id = self._context.get('website_id')
        for menu in self:
            if not current_website_id:
                menu.most_specific_child_ids = menu.child_id
            else:
                for child_menu in menu.child_id:
                    if (child_menu.website_id and child_menu.website_id.id == current_website_id) or\
                       (not child_menu.website_id and not any(menu.url == child_menu.url and menu.website_id.id == current_website_id for menu in menu.child_id)):
                        menu.most_specific_child_ids |= child_menu

    # used when getting menus for EditMenuDialog
    # reimplement entirely because there's no way to clean fix this
    @api.model
    def get_tree(self, website_id, menu_id=None):
        super(Menu, self).get_tree(website_id, menu_id=menu_id)
        def make_tree(node):
            page_id = node.page_id.id if node.page_id else None
            is_homepage = page_id and self.env['website'].browse(website_id).homepage_id.id == page_id
            menu_node = dict(
                id=node.id,
                name=node.name,
                url=node.page_id.url if page_id else node.url,
                new_window=node.new_window,
                sequence=node.sequence,
                parent_id=node.parent_id.id,
                children=[],
                is_homepage=is_homepage,
            )
            for child in node.most_specific_child_ids:  # website_multi: this is the only line that changed
                menu_node['children'].append(make_tree(child))
            return menu_node
        if menu_id:
            menu = self.browse(menu_id)
        else:
            menu = self.env['website'].browse(website_id).menu_id
        return make_tree(menu)

    @api.multi
    def _is_published_on_current_website(self):
        self.ensure_one()
        return not self.website_id or self.website_id.id == self._context.get('website_id')

    @api.multi
    def _create_website_specific_menus(self, websites):
        website_specific_menus = self.env['website.menu']

        for menu in self:
            assert not menu.website_id, '{} is not a generic menu, it belongs to {}'.format(menu, menu.website_id)
            for website_needing_menu in websites:
                website_specific_menus |= menu.copy({'website_id': website_needing_menu.id})

        return website_specific_menus

    @api.multi
    def unlink(self):
        '''COW for website.menu.'''
        Website = self.env['website']
        current_website_id = self._context.get('website_id')

        if current_website_id and not self._context.get('no_cow'):
            for menu in self:
                if Website.search_count([]) > 1 and not menu.website_id:
                    menu._create_website_specific_menus(Website.search([('id', '!=', current_website_id)]))

        return super(Menu, self).unlink()

    @api.multi
    def write(self, vals):
        '''COW for website.menu.'''
        current_website = self.env['website'].browse(self._context.get('website_id'))

        if current_website and not self._context.get('no_cow'):
            for menu in self:
                if not menu.website_id:
                    self -= menu
                    super(Menu, menu._create_website_specific_menus(current_website)).write(vals)

        return super(Menu, self).write(vals)


class WebsitePublishedMixin(models.AbstractModel):
    _inherit = 'website.published.mixin'

    published_on_website_ids = fields.Many2many('website', help='Determines on what websites this record will be visible.')
    website_published = fields.Boolean('Visible on current website',
                                       compute='_compute_website_published',
                                       inverse='_inverse_website_published',
                                       search='_search_website_published')

    @api.multi
    def _compute_website_published(self):
        for record in self:
            current_website_id = self._context.get('website_id')
            if current_website_id:
                record.website_published = current_website_id in record.published_on_website_ids.ids
            else:  # should be in the backend, return things that are published anywhere
                record.website_published = bool(record.published_on_website_ids)

    @api.multi
    def _inverse_website_published(self):
        for record in self:
            current_website_id = self._context.get('website_id')
            if current_website_id:
                current_website = self.env['website'].browse(current_website_id)

                if record.website_published:
                    record.published_on_website_ids |= current_website
                else:
                    record.published_on_website_ids -= current_website

            else:  # this happens when setting e.g. demo data, publish on all
                if record.website_published:
                    record.published_on_website_ids = self.env['website'].search([])
                else:
                    record.published_on_website_ids = False

    def _search_website_published(self, operator, value):
        if not isinstance(value, bool) or operator not in ('=', '!='):
            _logger.warning('unsupported search on website_published: %s, %s', operator, value)
            return [()]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            value = not value

        current_website_id = self._context.get('website_id')
        if current_website_id:
            return [('published_on_website_ids', 'in' if value is True else 'not in', current_website_id)]
        else:  # should be in the backend, return things that are published anywhere
            return [('published_on_website_ids', '!=' if value is True else '=', False)]

    @api.multi
    def website_publish_button(self):
        if self.env['website'].search_count([]) <= 1:
            return super(WebsitePublishedMixin, self).website_publish_button()
        else:
            # Some models using the mixin put the base url in the
            # website_url (e.g. website_slides' slide.slide), other
            # ones use a relative url (e.g. website_sale's
            # product.template). Since we are going to construct the
            # urls ourselves filter that out.
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            self.website_url = self.website_url.replace(base_url, '')

            wizard = self.env['website.urls.wizard'].create({
                'path': self.website_url,
                'record_id': self.id,
                'model_name': self._name,
            })
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'website.urls.wizard',
                'views': [(False, 'form')],
                'res_id': wizard.id,
                'target': 'new',
            }

    @api.multi
    def toggle_publish(self):
        for record in self:
            record.website_published = not record.website_published
