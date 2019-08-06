# coding: utf-8

import logging

from odoo import api, fields, models

class WebsitePublishedWizard(models.TransientModel):
    _name = 'website.urls.wizard'

    path = fields.Char(readonly=True)
    record_id = fields.Integer(required=True, readonly=True)
    model_name = fields.Char(required=True, readonly=True)
    website_urls = fields.One2many('website.url', 'wizard_id')

    @api.model
    def create(self, vals):
        res = super(WebsitePublishedWizard, self).create(vals)

#         for website in self.env['website'].search([]):
        for website in self.env['website'].search([('company_id','=',self.env.user.company_id.id)]):
            # todo jov fix port somehow
            self.env['website.url'].create({
                'wizard_id': res.id,
                'url': 'http://%s%s' % (website.domain, res.path if res.path != '#' else ''),
                'display_goto': res.path != '#',
                'website_id': website.id,
                'record_id': res.record_id,
                'model_name': res.model_name,
            })
        return res
