# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    is_request_spare_parts = fields.Boolean("Request Spare Parts", default=False, help="Allow Request Spare Parts in this stage.")
    is_return_and_refund = fields.Boolean("Return And Refund Device", default=False, help="Allow Return And Refung device in this stage.")
    is_replace_and_invoice = fields.Boolean("Replace And Generate Invoice", default=False, help="Allow replace and invoice generation in this stage.")
    is_create_quotation = fields.Boolean("Create Quotation", default=False, help="Allow create quotation in this stage.")
    allow_delete = fields.Boolean("Allow Delete", default=False, help="Job Card can be deleted in this stage.")
