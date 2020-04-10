# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class POSSession(models.Model):
    _inherit = 'pos.session'

    branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.user.branch_id)
