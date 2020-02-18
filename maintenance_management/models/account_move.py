# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    jobcard_ticket_id = fields.Many2one("helpdesk.ticket", string="Job Card", help="Related Job Card.")
