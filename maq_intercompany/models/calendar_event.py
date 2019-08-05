# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    company_id = fields.Many2one(related="user_id.company_id", string="Company", store=True)

    @api.model
    def calendar_for_employees(self):
        ''' Improved the calendar list view and added the custom domain to existing record rule
        '''
        rule_id = self.env.ref("calendar.calendar_event_rule_employee")
        if rule_id.domain_force:
            rule_id.update({'domain_force': "[('company_id','in', user.company_ids.ids)]"})
