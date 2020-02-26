# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get("filter_spare_parts", False):
            if self._context.get("ticket_product_id", False):
                ticket_product = self.browse(self._context.getd("ticket_product_id"))
                args = expression.AND([
                    args or [],
                    [('id', 'in', ticket_product.spare_part_product_ids.ids)]
                ])
            else:
                args = expression.AND([
                    args or [],
                    [('id', 'in', [])]
                ])
        return super(ProductProduct, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                        name_get_uid=name_get_uid)
