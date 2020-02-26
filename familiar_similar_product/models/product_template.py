# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_spare_part_product = fields.Boolean("Spare Part", default=False, help="This product is spare part product.")
    spare_part_product_ids = fields.Many2many("product.product", "product_template_spare_part_rel", "product_tmpl_id",
                                              "spare_part_id", string="Spare Parts", help="Spare Parts Of Product.")
    similar_product_ids = fields.Many2many("product.product", "similar_product_template_rel", "product_tmpl_id",
                                           "spare_part_id", string="Similar Products", compute="get_similar_products",
                                           store=False, help="Similar Product.")

    def get_similar_products(self):
        similar_product_obj = self.env["similar.product"]
        for product_template in self:
            for product in product_template.product_variant_ids:
                similar_products = similar_product_obj.search([("product_ids", "in", product.id)])
                similar_product_ids = similar_products.mapped("product_ids") - product
                product_template.similar_product_ids = [(6, 0, similar_product_ids.ids)]
