# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression
from odoo.tools import float_compare, float_round, float_repr
from datetime import datetime, timedelta


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    '''
    Override the move lines method and return the move lines in ascending order
    '''

    def get_move_lines_for_reconciliation(self, partner_id=None, excluded_ids=None, str=False, offset=0, limit=None, additional_domain=None, overlook_partner=False):
        """ Return account.move.line records which can be used for bank statement reconciliation.

            :param partner_id:
            :param excluded_ids:
            :param str:
            :param offset:
            :param limit:
            :param additional_domain:
            :param overlook_partner:
        """
        if partner_id is None:
            partner_id = self.partner_id.id

        # Blue lines = payment on bank account not assigned to a statement yet
        reconciliation_aml_accounts = [
            self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id]
        domain_reconciliation = ['&', '&', ('statement_line_id', '=', False), (
            'account_id', 'in', reconciliation_aml_accounts), ('payment_id', '<>', False)]

        # Black lines = unreconciled & (not linked to a payment or open balance
        # created by statement
        domain_matching = [('reconciled', '=', False)]
        if partner_id or overlook_partner:
            domain_matching = expression.AND([domain_matching, ['|', ('account_id.internal_type', 'in', [
                                             'payable', 'receivable']), '&', ('account_id.internal_type', '=', 'other'), ('account_id.reconcile', '=', True)]])
        else:
            # TODO : find out what use case this permits (match a check
            # payment, registered on a journal whose account type is other
            # instead of liquidity)
            domain_matching = expression.AND(
                [domain_matching, [('account_id.reconcile', '=', True)]])

        # Let's add what applies to both
        domain = expression.OR([domain_reconciliation, domain_matching])
        if partner_id and not overlook_partner:
            domain = expression.AND(
                [domain, [('partner_id', '=', partner_id)]])

        # Domain factorized for all reconciliation use cases
        if str:
            str_domain = self.env[
                'account.move.line'].domain_move_lines_for_reconciliation(str=str)
            if not partner_id:
                str_domain = expression.OR(
                    [str_domain, [('partner_id.name', 'ilike', str)]])
            domain = expression.AND([domain, str_domain])
        if excluded_ids:
            domain = expression.AND([[('id', 'not in', excluded_ids)], domain])

        # Domain from caller
        if additional_domain is None:
            additional_domain = []
        else:
            additional_domain = expression.normalize_domain(additional_domain)
        domain = expression.AND([domain, additional_domain])
        return self.env['account.move.line'].search(domain, offset=offset, limit=limit, order="date_maturity asc, id asc")

    '''
    Returns the move line for reconciliation proposition in ascending order wise
    Returns move line if the date of move line matches with bank statement line date.
    If the date does not match, then brings the move line from range of 3 days before or after the bank statement line date.
    If there are no records of move lines, 3 days before or after, then move line will be returned in ascending order
    Some print statements are there in commented state which can be removed if you want to check some values
    '''

    def get_reconciliation_proposition(self, excluded_ids=None):
        """ Returns move lines that constitute the best guess to reconcile a statement line
            Note: it only looks for move lines in the same currency as the statement line.
        """
        self.ensure_one()
        if not excluded_ids:
            excluded_ids = []
        amount = self.amount_currency or self.amount
        company_currency = self.journal_id.company_id.currency_id
        st_line_currency = self.currency_id or self.journal_id.currency_id
        currency = (st_line_currency and st_line_currency !=
                    company_currency) and st_line_currency.id or False
        precision = st_line_currency and st_line_currency.decimal_places or company_currency.decimal_places
        date_maturity = self.date
        if date_maturity:
            date_maturity = datetime.strptime(date_maturity, "%Y-%m-%d")
        params = {'company_id': self.env.user.company_id.id,
                  'account_payable_receivable': (self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id),
                  'amount': float_repr(float_round(amount, precision_digits=precision), precision_digits=precision),
                  'partner_id': self.partner_id.id,
                  'excluded_ids': tuple(excluded_ids),
                  'maturity_date': date_maturity,
                  'ref': self.name,
                  }
        account_mv_ln = self.env['account.move.line']
        aml_search = None
        if params.get('partner_id'):
            aml_search = account_mv_ln.search(['|', '&', '&', '&', ('date_maturity', '=', params.get('maturity_date')),
                                               ('partner_id', '=',
                                                params.get('partner_id')),
                                               ('payment_id', '!=', False),
                                               ('statement_line_id', '=', False),
                                               ('id', 'not in', excluded_ids),
                                               ('amount_residual', '=', params.get('amount'))], limit=1)
        else:
            aml_search = account_mv_ln.search([('date_maturity', '=', params.get('maturity_date')),
                                               ('payment_id', '!=', False),
                                               ('statement_line_id', '=', False),
                                               ('id', 'not in', excluded_ids),
                                               ('amount_residual', '=', params.get('amount'))], limit=1)
        aml_date_maturity = False
        date_maturity_before = date_maturity_after = False
        aml_date_mat_before = aml_date_mat_after = False
        date_maturity_before_max_dt = date_maturity_after_max_dt = False
        if aml_search.date_maturity:
            aml_date_maturity = datetime.strptime(
                aml_search.date_maturity, "%Y-%m-%d")
        if not aml_search:
            date_maturity_before_range = 5
            date_maturity_after_range = 5
            date_maturity_before_range_list = []
            date_maturity_after_range_list = []
            date_maturity_before_date_list = []
            date_maturity_after_date_list = []
            date_maturity_before_list = []
            date_maturity_after_list = []

            for rng in range(1, date_maturity_before_range + 1):
                date_maturity_before_range_list.append(rng)
            for rng in range(1, date_maturity_after_range + 1):
                date_maturity_after_range_list.append(rng)
            for dt_bef in date_maturity_before_range_list:
                date_maturity_bef = datetime.strftime(
                    date_maturity - timedelta(dt_bef), '%Y-%m-%d')
                date_maturity_bef = datetime.strptime(
                    date_maturity_bef, "%Y-%m-%d")
                date_maturity_before_date_list.append(date_maturity_bef)
            for dt_aft in date_maturity_after_range_list:
                date_maturity_aft = datetime.strftime(
                    date_maturity + timedelta(dt_aft), '%Y-%m-%d')
                date_maturity_aft = datetime.strptime(
                    date_maturity_aft, "%Y-%m-%d")
                date_maturity_after_date_list.append(date_maturity_aft)
            for date_before in date_maturity_before_date_list:
                aml_search_date_mat_bef = account_mv_ln.search([('date_maturity', '=', date_before),
                                                                ('payment_id',
                                                                 '!=', ''),
                                                                ('statement_line_id',
                                                                 '=', False),
                                                                ('id', 'not in',
                                                                 excluded_ids),
                                                                ('amount_residual', '=', params.get('amount'))], limit=1)
                if aml_search_date_mat_bef.date_maturity and aml_search_date_mat_bef.payment_id:
                    date_maturity_before_list.append(
                        aml_search_date_mat_bef.date_maturity)
            for date_after in date_maturity_after_date_list:
                aml_search_date_mat_aft = account_mv_ln.search([('date_maturity', '=', date_after),
                                                                ('payment_id',
                                                                 '!=', ''),
                                                                ('statement_line_id',
                                                                 '=', False),
                                                                ('id', 'not in',
                                                                 excluded_ids),
                                                                ('amount_residual', '=', params.get('amount'))], limit=1)
                if aml_search_date_mat_aft.date_maturity and aml_search_date_mat_aft.payment_id:
                    date_maturity_after_list.append(
                        aml_search_date_mat_aft.date_maturity)
            date_maturity_before_dt_tm_list = [datetime.strptime(
                date, '%Y-%m-%d') for date in date_maturity_before_list]
            date_maturity_after_dt_tm_list = [datetime.strptime(
                date, '%Y-%m-%d') for date in date_maturity_after_list]
            if date_maturity_before_dt_tm_list:
                """ Search for maximum from dates list which are before maturity date and update in params"""
#                 date_maturity_before_max_dt = max(date_maturity_before_dt_tm_list)
#                 params.update({'date_maturity_before_max_dt': date_maturity_before_max_dt})
                params.update(
                    {'date_maturity_before_dt_tm_list': date_maturity_before_dt_tm_list})
            if date_maturity_after_dt_tm_list:
                """ Search for minimum from dates list which are after maturity date and update in params"""
#                 date_maturity_after_max_dt = min(date_maturity_after_dt_tm_list)
#                 params.update({'date_maturity_after_max_dt': date_maturity_after_max_dt})
                params.update(
                    {'date_maturity_after_dt_tm_list': date_maturity_after_dt_tm_list})

            '''The below code is commented and IT can be used if u want to short the range of days from 3 to 1
            -------------------------------------------------------------------------------------'''
#             date_maturity_before = datetime.strftime(date_maturity - timedelta(1), '%Y-%m-%d')
#             date_maturity_before = datetime.strptime(date_maturity_before, "%Y-%m-%d")
#             date_maturity_after = datetime.strftime(date_maturity + timedelta(1), '%Y-%m-%d')
#             date_maturity_after = datetime.strptime(date_maturity_after, "%Y-%m-%d")
#             params.update({'date_maturity_after': date_maturity_after, 'date_maturity_before': date_maturity_before})
            '''----------------------------------------------------------------------------------'''
            """ The below code is commented and can be used for date range first ascending then descending from
                bank statement line date and search for account move line date
                ---------------------------------------------------------------------------------"""

#             aml_search_date_mat_before = account_mv_ln.search([('date_maturity','=',params.get('date_maturity_before_max_dt')),
#                                            ('payment_id', '!=', ''),
#                                            ('id', 'not in', excluded_ids),
#                                            ('amount_residual','=',params.get('amount'))], limit=1)
#             aml_search_date_mat_after = account_mv_ln.search([('date_maturity','=',params.get('date_maturity_after_max_dt')),
#                                            ('payment_id', '!=', ''),
#                                            ('id', 'not in', excluded_ids),
#                                            ('amount_residual','=',params.get('amount'))], limit=1)
#             if aml_search_date_mat_before.date_maturity:
#                 aml_date_mat_before = datetime.strptime(aml_search_date_mat_before.date_maturity, "%Y-%m-%d")
#             if aml_search_date_mat_after.date_maturity:
#                 aml_date_mat_after = datetime.strptime(aml_search_date_mat_after.date_maturity, "%Y-%m-%d")
            '''----------------------------------------------------------------------------------'''
        # Look for structured communication match
        if self.name:
            add_to_select = ", CASE WHEN aml.ref = %(ref)s THEN 1 ELSE 2 END as temp_field_order "
            add_to_from = " JOIN account_move m ON m.id = aml.move_id "
            select_clause, from_clause, where_clause = self._get_common_sql_query(
                overlook_partner=True, excluded_ids=excluded_ids, split=True)
            sql_query = select_clause + add_to_select + \
                from_clause + add_to_from + where_clause
            sql_query += " AND (aml.ref= %(ref)s or m.name = %(ref)s) \
                    ORDER BY temp_field_order, date_maturity asc, aml.id asc"
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.fetchone()
            if results:
                return self.env['account.move.line'].browse(results[0])

        # Look for a single move line with the same amount
        field = currency and 'amount_residual_currency' or 'amount_residual'
        liquidity_field = currency and 'amount_currency' or amount > 0 and 'debit' or 'credit'
        liquidity_amt_clause = currency and '%(amount)s::numeric' or 'abs(%(amount)s::numeric)'
        '''count variables for elif condition date_maturity_before_dt_tm_list and date_maturity_after_dt_tm_list'''
        count_less = 1
        count_greater = 1
        loop_count = 1
        if aml_date_maturity and date_maturity == aml_date_maturity:
            sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                " AND date_maturity = %(maturity_date)s AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                  ORDER BY date_maturity asc, aml.id asc LIMIT 1"
        elif params.get('date_maturity_before_dt_tm_list') or params.get('date_maturity_after_dt_tm_list'):
            ls_less = params.get('date_maturity_before_dt_tm_list') or []
            ls_great = params.get('date_maturity_after_dt_tm_list') or []
            ls = ls_less + ls_great
            dt = date_maturity
            if ls:
                for l in ls:
                    if (date_maturity - timedelta(count_less)) in ls_less and len(ls_less) > 1:
                        date_maturity_before_dt = date_maturity - \
                            timedelta(count_less)
                        params.update(
                            {'date_maturity_before_dt': date_maturity_before_dt})
                        sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                            " AND date_maturity = %(date_maturity_before_dt)s AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                          ORDER BY date_maturity asc, aml.id asc LIMIT 1"
                        break
                    elif (date_maturity + timedelta(count_greater)) in ls_great and len(ls_great) > 1:
                        date_maturity_after_dt = date_maturity + \
                            timedelta(count_greater)
                        params.update(
                            {'date_maturity_after_dt': date_maturity_after_dt})
                        sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                            " AND date_maturity = %(date_maturity_after_dt)s AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                          ORDER BY date_maturity asc, aml.id asc LIMIT 1"
                        break
                    elif len(ls_less) <= 1 and len(ls_great) <= 1:
                        if len(ls_less) == 1:
                            date_maturity_before_single_dt = ls_less[0]
                            params.update(
                                {'date_maturity_before_single_dt': date_maturity_before_single_dt})
                            sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                                " AND date_maturity = %(date_maturity_before_single_dt)s AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                              ORDER BY date_maturity asc, aml.id asc LIMIT 1"
                            break
                        elif len(ls_great) == 1:
                            date_maturity_after_single_dt = ls_great[0]
                            params.update(
                                {'date_maturity_after_single_dt': date_maturity_after_single_dt})
                            sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                                " AND date_maturity = %(date_maturity_after_single_dt)s AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                              ORDER BY date_maturity asc, aml.id asc LIMIT 1"
                            break
                    count_less += 1
                    count_greater += 1
                    loop_count += 1
                    if loop_count == len(ls):
                        count_less = count_greater = loop_count = 1
                        break
            """ Use the below code if you want to revert back to the date before and then date after scenario
            ----------------------------------------------------------------------------------"""
#         elif params.get('date_maturity_before_max_dt') or params.get('date_maturity_after_max_dt'):
#             if (aml_date_mat_after and aml_date_mat_before) or \
#                 (aml_date_mat_before and params.get('date_maturity_before_max_dt') ==\
#                  aml_date_mat_before):
#                 sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
#                     " AND date_maturity = %(date_maturity_before_max_dt)s AND aml.payment_id IS NOT NULL AND ("+field+" = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND "+liquidity_field+" = " + liquidity_amt_clause + ")) \
#                       ORDER BY date_maturity asc, aml.id asc LIMIT 1"
#             elif aml_date_mat_after and params.get('date_maturity_after_max_dt') == aml_date_mat_after:
#                 sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
#                     " AND date_maturity = %(date_maturity_after_max_dt)s AND aml.payment_id IS NOT NULL AND ("+field+" = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND "+liquidity_field+" = " + liquidity_amt_clause + ")) \
#                       ORDER BY date_maturity asc, aml.id asc LIMIT 1"
            '''----------------------------------------------------------------------------------'''
        else:
            sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
                " AND aml.payment_id IS NOT NULL AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                    ORDER BY date_maturity asc, aml.id asc LIMIT 1"
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchone()
        if results:
            return self.env['account.move.line'].browse(results[0])

        return self.env['account.move.line']
