# -*- coding: utf-8 -*-

from odoo import models, fields, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import Warning


class Sale(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[('hold', 'Hold'),
                                            ('sent_for_approval', 'Sent For Approval'),
                                            ('approved_by_sales_manager', 'Approved By Sales Manager'),
                                            ('request_rejected', 'Request Rejected'),
                                            ])

    def _get_matured_due_amount(self, date_from):
        cr = self.env.cr
        company_ids = self.env.context.get('company_ids', (self.env.user.company_id.id,))
        args_list = (self.partner_id.id, date_from, tuple(company_ids))

        query = '''SELECT
                        sum(am.amount_residual)
                    FROM
                        account_move_line AS l inner join account_move am on (l.move_id = am.id)
                    WHERE
                        (am.state IN ('draft','posted'))
                        AND (l.account_internal_type = 'receivable')
                        AND (am.partner_id = %s)
                        AND (l.date_maturity <= %s)
                        AND am.company_id IN %s
                        AND am.amount_residual > 0.0'''
        cr.execute(query, args_list)
        due_amount_rec = cr.fetchall()
        due_amount = due_amount_rec and due_amount_rec[0] and due_amount_rec[0][0] or 0.0

        if due_amount > 0:
            return due_amount
        return 0.0
            
    def check_credit_limit_exceeded(self):
        customer_credit_limit = self.partner_id.credit_limit
        credit_limit_exceeded = False
        credit_duration_exceeded = False
        if customer_credit_limit > 0.0:
            due_amount_after_confirm_order = self.partner_id.credit or 0.0

            due_amount_after_confirm_order += sum(self.partner_id.sale_order_ids.mapped("invoice_ids").filtered(
                lambda invoice: invoice.state == 'draft' and invoice.amount_total > 0).mapped("amount_total"))

            due_amount_after_confirm_order += sum(self.partner_id.sale_order_ids.filtered(
                lambda order_id: order_id.state in ['sale', 'done'] and not order_id.invoice_ids).mapped("amount_total"))

            due_amount_after_confirm_order += self.amount_total

            if customer_credit_limit < due_amount_after_confirm_order:
                credit_limit_exceeded = True

            date_from = "%s" % datetime.now().date()
            matured_due_amount = self._get_matured_due_amount(date_from)
            if matured_due_amount > 0.0:
                credit_duration_exceeded = True

            confirmed_orders_without_invoice = self.partner_id.sale_order_ids.filtered(
                lambda order: order.state in ['sale', 'done'] and order.amount_total > 0.0 and not order.invoice_ids)
            if confirmed_orders_without_invoice:
                for order in confirmed_orders_without_invoice:
                    payment_duration = order.partner_id.property_payment_term_id and max(
                        order.partner_id.property_payment_term_id.line_ids.mapped("days")) or 0.0
                    due_date = order.date_order + relativedelta(days=payment_duration)
                    if due_date.date() <= datetime.now().date():
                        credit_duration_exceeded = True
                        break

        return credit_limit_exceeded, credit_duration_exceeded

    def action_confirm(self):
        for record in self:
            if record.state in ['draft', 'sent']:
                credit_limit_exceeded, credit_duration_exceeded = record.check_credit_limit_exceeded()
                if credit_limit_exceeded or credit_duration_exceeded:
                    self -= record
                    record.state = "hold"
        self and super(Sale, self).action_confirm()
        return True

    def credit_limit_exceed_request(self):
        return self.write({"state": "sent_for_approval"})

    def approve_sale_manager(self):
        credit_limit_exceeded, credit_duration_exceeded = self.check_credit_limit_exceeded()
        if credit_duration_exceeded and credit_limit_exceeded and not self.env.user.has_group("base.group_erp_manager"):
            raise Warning(_("You can not approve request when customer exceed credit limit and credit duration both."))
        return self.write({"state": "approved_by_sales_manager"})

    def approve_account_manager(self):
        credit_limit_exceeded, credit_duration_exceeded = self.check_credit_limit_exceeded()
        if credit_duration_exceeded and credit_limit_exceeded and not self.env.user.has_group("base.group_erp_manager"):
            raise Warning(_("You can not approve request when customer exceed credit limit and credit duration both."))
        return self.action_confirm()

    def reject_request(self):
        return self.write({"state": "request_rejected"})
