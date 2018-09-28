# coding: utf-8

import logging

from odoo import api, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _login(cls, db, login, password):
        """
            override to allow user to login based on their allowed company's website
            for example -
            Maq users should not be able to use their login to login through the joint portal and
            vice versa (joint user should not be able to login to portal using Maq website)
            unless they are a user with access to both companies.

            UPDATE CHANGES ARE MARKED WITH 'CUSTOM'
        """
        #TODO - can we use registered_on_website_id field of res users?
        if not password:
            return False
        user_id = False
        try:
            with cls.pool.cursor() as cr:
                self = api.Environment(cr, SUPERUSER_ID, {})[cls._name]
                user = self.search([('login', '=', login)])
                # CUSTOM START
                if user:
                    current_website_id = self.env['website'].get_current_website()
                    if current_website_id.company_id.id not in user.company_ids.ids:
                        user = False
                # CUSTOM END
                if user:
                    user_id = user.id
                    user.sudo(user_id).check_credentials(password)
                    user.sudo(user_id)._update_last_login()
        except AccessDenied:
            user_id = False

        status = "successful" if user_id else "failed"
        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info("Login %s for db:%s login:%s from %s", status, db, login, ip)

        return user_id
