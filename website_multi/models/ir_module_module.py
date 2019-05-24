# coding: utf-8

import logging
import os
import re

from odoo import api, fields, models
from odoo.modules import load_information_from_description_file
from odoo.tools import convert_file

_logger = logging.getLogger(__name__)


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    data_directory_name = fields.Char()
    website_id = fields.Many2one('website')
    is_installed_on_current_website = fields.Boolean(compute='_compute_is_installed_on_current_website')

    @api.multi
    @api.depends('website_id')
    def _compute_is_installed_on_current_website(self):
        for module in self:
            module.is_installed_on_current_website = self.env['website'].get_current_website() == module.website_id

    def _get_records(self, model):
        external_ids = self.env['ir.model.data'].search([('module', '=', self.name), ('model', '=', model)])
        return self.env[model].browse(external_ids.mapped('res_id'))

    @api.multi
    def _make_data_website_local(self):
        for module in self:
            install_on_website = self.env['website'].get_current_website()
            module = module.with_context(no_cow=True)

            if not install_on_website:
                _logger.info('no website specified, so not making records website local')
                return

            for view in module._get_records('ir.ui.view'):
                if not view.website_id:
                    view.website_id = install_on_website
                # sometimes themes contain hardcoded references to their module name
                view.arch_db = re.sub(r'\b%s\.' % module.data_directory_name, '%s.' % module.name, view.arch_db)

            # can't write in one 'write' because of ensure_one in write of website.page
            for page in module._get_records('website.page'):
                if not page.website_id:
                    page.website_ids = install_on_website

            for menu in module._get_records('website.menu'):
                if not menu.website_id:
                    menu.website_id = install_on_website

            module.website_id = install_on_website

    def _get_installed_themes_domain(self):
        return [
            ('state', '=', 'installed'),
            ('name', 'ilike', '%theme%'),
        ]

    @api.multi
    def button_choose_theme(self):
        install_on_website = self.env['website'].get_current_website()
        theme_category = self.env.ref('base.module_category_theme', False)
        hidden_category = self.env.ref('base.module_category_hidden', False)
        theme_hidden_category = self.env.ref('base.module_category_theme_hidden', False)

        theme_category_id = theme_category.id if theme_category else 0
        hidden_categories_ids = [hidden_category.id if hidden_category else 0, theme_hidden_category.id if theme_hidden_category else 0]

        if self.state == 'installed':
            _logger.info('creating website local child module')
            return self.copy({
                'name': self.name + '_for_website_%s' % install_on_website.id,
                'shortdesc': self.shortdesc + ' (for %s)' % install_on_website.name,
                'data_directory_name': self.name,
            }).button_choose_theme()

        modules_to_uninstall = self.search([  # Uninstall the theme(s) which is (are) installed
            ('state', '=', 'installed'),
            ('website_id', '=', install_on_website.id),
            '|', ('category_id', 'not in', hidden_categories_ids), ('name', '=', 'theme_default'),
            '|', ('category_id', '=', theme_category_id), ('category_id.parent_id', '=', theme_category_id)
        ])

        child_modules = self.env['ir.module.module']
        if modules_to_uninstall:
            child_modules = self.search([('data_directory_name', 'in', modules_to_uninstall.mapped('name'))])  # todo jov reinstall these on their websites

        (modules_to_uninstall | child_modules).button_immediate_uninstall()

        installed_themes_domain = self._get_installed_themes_domain()
        themes_installed_before = self.search(installed_themes_domain)
        next_action = self.button_immediate_install()  # Then install the new chosen one
        themes_installed_after = self.search(installed_themes_domain)

        (themes_installed_after - themes_installed_before)._make_data_website_local()

        if next_action.get('tag') == 'reload' and not next_action.get('params', {}).get('menu_id'):
            next_action = self.env.ref('website.action_website').read()[0]

        return next_action

    @api.multi
    def button_immediate_uninstall(self):
        installed_themes_domain = self._get_installed_themes_domain()
        themes_installed_before = self.search(installed_themes_domain)

        modules_to_uninstall = self | self.search([('name', '=', self.data_directory_name)], limit=1)
        res = super(IrModuleModule, modules_to_uninstall).button_immediate_uninstall()
        themes_installed_after = self.search(installed_themes_domain)

        uninstalled_themes = themes_installed_before - themes_installed_after
        uninstalled_themes.write({'website_id': False})

        return res

    @api.multi
    def module_uninstall(self):
        res = super(IrModuleModule, self).module_uninstall()
        # the uninstall wizard has a module_id field that's required
        self.env['base.module.uninstall'].search([]).unlink()
        # remove uninstalled child modules
        self.filtered('data_directory_name').unlink()
        return res

    @api.multi
    def button_immediate_install(self):
        install_on_website = self.env['website'].get_current_website()

        for module in self:
            parent_module = self.search([('name', '=', module.data_directory_name)], limit=1)
            if parent_module and parent_module.state == 'installed' and install_on_website:
                terp = load_information_from_description_file(parent_module.name)
                for kind in ['data', 'init_xml', 'update_xml']:
                    for filename in terp[kind]:
                        ext = os.path.splitext(filename)[1].lower()
                        _logger.info("module %s: loading %s", module.name, filename)
                        noupdate = False
                        if ext == '.csv' and kind in ('init', 'init_xml'):
                            noupdate = True
                        pathname = os.path.join(parent_module.name, filename)
                        convert_file(self.env.cr, module.name, filename, {}, mode='init', noupdate=noupdate, kind=kind, pathname=pathname)
                        module.state = 'installed'
            else:
                super(IrModuleModule, module).button_immediate_install()

        menu = self.env['ir.ui.menu'].search([('parent_id', '=', False)])[:1]
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }
