# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    warranty_id = fields.Many2one('warranty.template', string="Warranty Template")
