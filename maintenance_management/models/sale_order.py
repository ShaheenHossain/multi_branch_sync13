# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_installation_product = fields.Boolean("Has Installation Product", compute="get_installation_product", store=False)
    jobcard_count = fields.Integer("Jobcard Count", compute="get_jobcard_count", store=False)
    job_card_id = fields.Many2one("helpdesk.ticket", string="Job Card", help="Related Job Card Reference")

    def get_jobcard_count(self):
        for order in self:
            order.jobcard_count = len(order.order_line.mapped("jobcard_id").ids)

    def get_installation_product(self):
        for order in self:
            if True in order.order_line.filtered(lambda line: not line.jobcard_id).mapped("product_id").mapped("product_tmpl_id").mapped("is_installation_product"):
                order.has_installation_product = True
            else:
                order.has_installation_product = False

    def create_installation_jobcards(self):
        jobcard_obj = self.env["helpdesk.ticket"]
        for order in self:
            for line in order.order_line:
                if line.jobcard_id:
                    continue
                jobcard_fields = jobcard_obj.fields_get()
                jobcard_data = jobcard_obj.default_get(jobcard_fields)
                tmp_jobcard = jobcard_obj.new({
                    "product_id": line.product_id.id,
                    "sale_order_id": order.id,
                })
                tmp_jobcard.product_id_onchange()
                tmp_jobcard.sale_order_onchange()
                jobcard_vals = tmp_jobcard._convert_to_write(tmp_jobcard._cache)
                jobcard_vals.update({
                    "name": "%s Support" % line.product_id.display_name,
                    "branch_id": order.branch_id.id,
                    "partner_id": order.partner_id.id,
                    "is_job_card": True,
                    "job_card_type": "installation",
                })
                new_jobcard = jobcard_obj.create(jobcard_vals)

                if new_jobcard:
                    line.jobcard_id = new_jobcard.id
        return True

    def action_view_jobcard(self):
        action = self.env.ref('maintenance_management.jobcard_action').read()[0]
        jobcards = self.order_line.mapped("jobcard_id")
        if len(jobcards) > 1:
            action['domain'] = [('id', 'in', jobcards.ids)]
        elif jobcards:
            form_view = [(self.env.ref('maintenance_management.helpdesk_ticket_jobcard_inherit_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = jobcards.id
        return action


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    jobcard_id = fields.Many2one("helpdesk.ticket", string="Job Card", help="Related Jobcard.")
