# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class POSPayment(models.Model):
    _inherit = 'pos.payment'

    branch_id = fields.Many2one('res.branch', 'Branch')
