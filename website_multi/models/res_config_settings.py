# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    website_auth_signup_uninvited = fields.Selection(related='website_id.website_auth_signup_uninvited')
    website_template_user_id = fields.Many2one(related='website_id.website_template_user_id')
    website_user_id = fields.Many2one(related='website_id.user_id')
    website_company_id = fields.Many2one(related='website_id.company_id')

    @api.multi
    def open_template_user(self):
        super(ResConfigSettings, self).open_template_user()
        action = self.env.ref('base.action_res_users').read()[0]
        action['res_id'] = self.website_id.website_template_user_id.id
        action['views'] = [[self.env.ref('base.view_users_form').id, 'form']]
        return action
