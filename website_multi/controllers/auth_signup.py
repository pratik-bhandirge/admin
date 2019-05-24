# coding: utf-8

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request

class AuthSignupHome(AuthSignupHome):
    def get_auth_signup_config(self):
        res = super(AuthSignupHome, self).get_auth_signup_config()
        current_website = request.env['website'].get_current_website()
        res['signup_enabled'] = current_website.website_auth_signup_uninvited == 'b2c'
        return res
