# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    wh_scrap_location_id = fields.Many2one('stock.location', 'Scrap Location')
