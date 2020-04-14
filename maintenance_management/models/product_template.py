# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_installation_product = fields.Boolean("Installation Product", default=False, help="Does this product require installation?")
