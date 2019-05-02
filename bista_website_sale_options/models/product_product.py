
from odoo import models, fields, api


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    m_product_specification_ids = fields.One2many("product.specification.line","product_tmpl_id","Product Specifications")


class ProductSpecificationLine(models.Model):
    _name = "product.specification.line"
    _rec_name = 'attribute_id'

    product_tmpl_id = fields.Many2one('product.template', 'Product Template', ondelete='cascade', required=True)
    attribute_id = fields.Many2one('product.attribute', 'Attribute', ondelete='restrict', required=True)
    value_ids = fields.Many2many('product.attribute.value', string='Attribute Values')

    @api.constrains('value_ids', 'attribute_id')
    def _check_valid_attribute(self):
        if any(line.value_ids > line.attribute_id.value_ids for line in self):
            raise ValidationError(_('Error ! You cannot use this attribute with the following value.'))
        return True

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # TDE FIXME: currently overriding the domain; however as it includes a
        # search on a m2o and one on a m2m, probably this will quickly become
        # difficult to compute - check if performance optimization is required
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            args = args or []
            domain = ['|', ('attribute_id', operator, name), ('value_ids', operator, name)]
            return self.search(expression.AND([domain, args]), limit=limit).name_get()
        return super(ProductAttributeLine, self).name_search(name=name, args=args, operator=operator, limit=limit)