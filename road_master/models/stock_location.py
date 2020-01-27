# -*- coding: utf-8 -*-

from odoo import models, fields


class StockLocation(models.Model):
    _inherit = "stock.location"

    mobile_location = fields.Boolean("Mobile Location", copy=False, help="Mobile Location to transfer device to customer.")
