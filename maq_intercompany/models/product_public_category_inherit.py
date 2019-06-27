# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductPublicCategory(models.Model):

    _inherit = 'product.public.category'

    m_company_id = fields.Many2one("res.company", string="Company", compute="_compute_product_company", store=True)

    @api.depends("website_id", "parent_website_id", "parent_id")
    def _compute_product_company(self):
        for rec in self:
            if not rec.parent_id:
                rec.m_company_id = rec.website_id.company_id
            elif rec.parent_id:
                rec.m_company_id = rec.parent_id.website_id.company_id

