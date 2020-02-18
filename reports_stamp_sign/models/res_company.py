# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    company_stamp = fields.Binary(string="Company Stamp")
