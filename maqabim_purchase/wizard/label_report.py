# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class LabelReportWizard(models.TransientModel):

    _name = 'label.report.wizard'
    _description = 'Label Report'

    formats = fields.Selection([
        ('f1_v1', '4W x 20L v1'),
        ('f1_v2', '4W x 20L v2'),
        ('f2_v1', '2W x 5L v1'),
        ('f2_v2', '2W x 5L v2')
    ], string='Report Formats', default='f1_v1')

    report_label_type = fields.Selection([('sale', 'Sale'), ('purchase', 'Purchase'), ('picking', 'Picking')])

    @api.multi
    def print_report(self):
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        report = 'maqabim_purchase.report_po_label'
        if self.report_label_type == 'sale':
            report = 'maqabim_purchase.report_so_label'
        elif self.report_label_type == 'picking':
            report = 'maqabim_purchase.report_picking_label'
        return self.env.ref(report).with_context(from_transient_model=True).report_action([], data=data)
