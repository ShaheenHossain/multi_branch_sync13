# -*- coding: utf-8 -*-

from odoo import models, fields


class SimilarProduct(models.Model):
    _name = "similar.product"
    _description = "Similar Product"
    _order = "id desc"

    name = fields.Char("Name", required=True, copy=False, help="Name Of Similar Product Group.")
    product_ids = fields.Many2many("product.product", "smiliar_product_rel", "similar_product_id", "product_id",
                                   string="Products", help="Similar Products.")
