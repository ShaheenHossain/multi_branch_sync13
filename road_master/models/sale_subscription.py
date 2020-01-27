# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    renew_type = fields.Selection([("based_on_plate_expory_date", "Based On Plate Expiry Date"),
                                   ("based_on_last_plate_expiry_date", "Based On Last Plate Expiry Date")],
                                  string="Renew Type", copy=False, help="Renew type based on plates.")

    def set_to_renew(self):
        device_installation_line_obj = self.env["device.installation.line"]
        if self.renew_type == 'based_on_last_plate_expiry_date':
            device_installation_lines = device_installation_line_obj.search([('subscription_id', '=', self.id)])
            if not device_installation_lines:
                return super(SaleSubscription, self).set_to_renew()
            today = fields.Date.today()
            next_month = fields.Date.from_string(today) + relativedelta(months=1)
            installation_orders = device_installation_lines.mapped('device_installation_id').mapped('sale_order_id')
            device_installations = installation_orders.mapped('device_installation_ids')
            subscriptions = device_installations.mapped("device_installation_line_ids").mapped("subscription_id").filtered(lambda sub: sub.renew_type == 'based_on_last_plate_expiry_date')
            subscriptions_to_renew = subscriptions.filtered(lambda sub: sub.in_progress)
            last_plate_date = max(subscriptions_to_renew.mapped('date'))
            res=False
            if last_plate_date and last_plate_date < next_month:
                res = super(SaleSubscription, self).set_to_renew()
            return res

        return super(SaleSubscription, self).set_to_renew()

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        invoice_line_vals = super(SaleSubscription, self)._prepare_invoice_line(line, fiscal_position, date_start=date_start, date_stop=date_stop)
        if self.renew_type and self.renew_type == "based_on_last_plate_expiry_date":
            today = fields.Date.today()
            actual_end_date = self.date
            subscription_duration_days = 0
            if self.template_id.recurring_rule_type == 'daily':
                actual_end_date = self.date_start + relativedelta(days=self.template_id.recurring_interval)
                subscription_duration_days = 1
            elif self.template_id.recurring_rule_type == 'weekly':
                actual_end_date = self.date_start + relativedelta(weeks=self.template_id.recurring_interval)
                subscription_duration_days = 7
            elif self.template_id.recurring_rule_type == 'monthly':
                actual_end_date = self.date_start + relativedelta(months=self.template_id.recurring_interval)
                subscription_duration_days = ((today + relativedelta(months=1)) - today).days
            elif self.template_id.recurring_rule_type == 'yearly':
                actual_end_date = self.date_start + relativedelta(years=self.template_id.recurring_interval)
                subscription_duration_days = ((today + relativedelta(years=1)) - today).days
            date_difference = actual_end_date and today and today - actual_end_date or 0.0
            date_difference_days = date_difference and date_difference.days > 0 and date_difference.days or 0.0
            if date_difference_days:
                if invoice_line_vals:
                    price_unit = invoice_line_vals.get("price_unit")
                    new_price_unit = price_unit + ((price_unit / subscription_duration_days) * date_difference_days)
                    invoice_line_vals.update({"price_unit": new_price_unit})
        return invoice_line_vals
