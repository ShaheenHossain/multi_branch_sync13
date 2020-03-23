# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = "res.company"

    company_stamp = fields.Binary(string="Company Stamp")
    name = fields.Char(string="name", translate=True)
    arabic_name = fields.Char("Arabic Name")
    reports_footer = fields.Html("Arabic Footer")
