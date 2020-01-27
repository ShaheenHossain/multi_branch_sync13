# -*- coding: utf-8 -*-

from odoo import models,fields


class HardwareType(models.Model):
    _name = "hardware.type"
    _description = "Hardware Type"
    _order = "id desc"

    name = fields.Char("Name", required=True)
