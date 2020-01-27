# -*- coding: utf-8 -*-

from odoo import models,fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    device_installtion_line_id = fields.Many2one("device.installation.line", string="Device Installation Line",
                                                 copy=False, ondelete="restrict", help="Related Device Installation Line.")
