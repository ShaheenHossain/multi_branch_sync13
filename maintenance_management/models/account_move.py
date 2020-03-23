# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class AccountMove(models.Model):
    _inherit = "account.move"

    jobcard_ticket_id = fields.Many2one("helpdesk.ticket", string="Job Card", help="Related Job Card.")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        sale_obj = self.env["sale.order"]
        if self._context.get("jobcard_invoice_check", False):
            if self._context.get("sale_order_id", False):
                sale_order = sale_obj.browse(self._context.get("sale_order_id"))
                args = expression.AND([
                    args or [],
                    [('id', 'in', sale_order.invoice_ids.ids)]
                ])
            else:
                args = expression.AND([
                    args or [],
                    [('id', 'in', [])]
                ])
        return super(AccountMove, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                     name_get_uid=name_get_uid)
