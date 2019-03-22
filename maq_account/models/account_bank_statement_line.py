# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import float_compare, float_round, float_repr


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    '''
    Updated the move lines for reconciliation in ascending order 
    '''

    def get_move_lines_for_reconciliation(self, partner_id=None, excluded_ids=None, str=False, offset=0, limit=None, additional_domain=None, overlook_partner=False):
        res = super(AccountBankStatementLine, self).get_move_lines_for_reconciliation(
            partner_id, excluded_ids, str, offset, limit, additional_domain, overlook_partner)
        return res.sorted(lambda l: (l.date_maturity, l.id))

    '''
    Returns the move line for reconciliation proposition in ascending order wise 
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
        params = {'company_id': self.env.user.company_id.id,
                  'account_payable_receivable': (self.journal_id.default_credit_account_id.id, self.journal_id.default_debit_account_id.id),
                  'amount': float_repr(float_round(amount, precision_digits=precision), precision_digits=precision),
                  'partner_id': self.partner_id.id,
                  'excluded_ids': tuple(excluded_ids),
                  'ref': self.name,
                  }
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
        sql_query = self._get_common_sql_query(excluded_ids=excluded_ids) + \
            " AND (" + field + " = %(amount)s::numeric OR (acc.internal_type = 'liquidity' AND " + liquidity_field + " = " + liquidity_amt_clause + ")) \
                ORDER BY date_maturity asc, aml.id asc LIMIT 1"
        self.env.cr.execute(sql_query, params)
        results = self.env.cr.fetchone()
        if results:
            return self.env['account.move.line'].browse(results[0])

        return self.env['account.move.line']
