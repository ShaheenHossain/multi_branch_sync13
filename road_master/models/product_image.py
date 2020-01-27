# -*- coding: utf-8 -*-

from odoo import models,fields


class ProductImage(models.Model):
    _name = "product.image"
    _description = "ProductImage"
    _order = "id desc"

    name = fields.Char("Name")
    image = fields.Binary("Image", required=1)
    product_template_id = fields.Many2one("product.template", string="Product Template",
                                          help="Related Product Template.")
