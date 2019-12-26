# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_limit = fields.Float("Credit Limit", help="Credit Limit to manage customer outstanding debts.")
