# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_spare_part_product = fields.Boolean("Spare Part", default=False, help="This product is spare part product.")
