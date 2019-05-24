# coding: utf-8

import logging

from odoo import api, fields, models, _, registry, SUPERUSER_ID
from odoo.exceptions import AccessDenied, ValidationError
from odoo.tools.misc import ustr
from odoo.addons.auth_signup.models.res_partner import SignupError

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    registered_on_website_id = fields.Many2one('website')

    _sql_constraints = [
        # this is done in Python because a SQL constraint like UNIQUE
        # (login, registered_on_website_id) allows ('abc', NULL) and
        # ('abc', NULL) to coexist because of how SQL handles NULLs.
        ('login_key', 'CHECK (1=1)', 'You can not have two users with the same login!')
    ]

    @api.one
    @api.constrains('login', 'registered_on_website_id')
    def _check_login(self):
        if self.search([('id', '!=', self.id),
                        ('login', '=', self.login),
                        ('registered_on_website_id', '=', self.registered_on_website_id.id)]):
            raise ValidationError(_('You can not have two users with the same login!'))

    @classmethod
    def _login(cls, db, login, password):
        try:
            return super(ResUsers, cls)._login(db, login, password)
        except ValueError:
            _logger.info('multiple users with login %s', login)

        user_id = False
        with registry(db).cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            user = env['res.users'].browse(user_id)
            if user and not user.share:
                return user_id
            else:
                current_website_id = env['website'].get_current_website().id
                user = env['res.users'].search([('login', '=', login), ('registered_on_website_id', '=', current_website_id)])
                if user and current_website_id:
                    try:
                        user_id = user.id
                        user.sudo(user_id).check_credentials(password)
                        user.sudo(user_id)._update_last_login()
                    except AccessDenied:
                        _logger.info('Multi-website login failed for db:%s login:%s website_id:%s', db, login, current_website_id)
                        user_id = False
                else:
                    user_id = False
        return user_id

    # website_multi: note that this function does not prevent signup
    # in 'usual' cases. The signup link isn't rendered when signup is
    # disabled and the /web/signup controller returns a 404 if it's
    # disabled. So unless someone is doing something weird this
    # shouldn't be triggered.
    @api.model
    def _signup_create_user(self, values):
        """ create a new user from the template user """
        # website_multi: get the template user defined on website instead of system parameter
        current_website = self.env['website'].browse(self._context.get('website_id'))
        template_user = current_website.website_template_user_id
        assert template_user.exists(), 'Signup: invalid template user'

        # website_multi: also add website_id in context. We could also
        # create a template user per website but for now I don't think
        # it's necessary.
        values['registered_on_website_id'] = current_website.id

        # check that uninvited users may sign up
        if 'partner_id' not in values:
            if current_website.website_auth_signup_uninvited != 'b2c':
                raise SignupError(_('Signup is not allowed for uninvited users'))

        assert values.get('login'), "Signup: no login given for new user"
        assert values.get('partner_id') or values.get('name'), "Signup: no name or partner given for new user"

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = True
        try:
            with self.env.cr.savepoint():
                return template_user.with_context(no_reset_password=True).copy(values)
        except Exception as e:
            # copy may failed if asked login is not available.
            raise SignupError(ustr(e))
