# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = "product.product"

    spare_part_product_ids = fields.Many2many("product.product", "product_spare_part_rel", "product_id",
                                              "spare_part_id", string="Spare Parts", help="Spare Parts Of Product.")
    similar_product_ids = fields.Many2many("product.product", "similar_product_variant_rel", "product_id",
                                           "spare_part_id", string="Similar Products", compute="get_similar_products",
                                           store=False, help="Similar Product.")

    def get_similar_products(self):
        similar_product_obj = self.env["similar.product"]
        for product in self:
            similar_products = similar_product_obj.search([("product_ids", "in", product.id)])
            similar_product_ids = similar_products.mapped("product_ids") - product
            product.similar_product_ids = [(6, 0, similar_product_ids.ids)]

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
