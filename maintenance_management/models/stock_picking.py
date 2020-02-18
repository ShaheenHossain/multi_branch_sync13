# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    jobcard_ticket_id = fields.Many2one("helpdesk.ticket", string="Job Card", help="Related Job Card.")
    picking_id = fields.Many2one("stock.picking", "Transfer Request", help="Related Transfer Requests.")
    transfer_request_count = fields.Integer("Transfer Reqeust Count", compute="get_transfer_request_count", store=False)

    def get_transfer_request_count(self):
        for record in self:
            record.transfer_request_count = len(self.search([("picking_id", "=", record.id)]))

    def action_request_transfer(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.search([("picking_id", "=", self.id)])
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id,
                                 default_picking_id=picking_id.id,
                                 default_picking_type_id=picking_id.picking_type_id.id, default_origin=self.name,
                                 default_group_id=picking_id.group_id.id)
        return action
