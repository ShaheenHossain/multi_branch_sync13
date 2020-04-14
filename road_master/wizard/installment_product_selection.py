# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class InstallmentProductSelection(models.TransientModel):
    _name = "installation.product.selection"
    _description = "Installment Product Selection"


    sale_order_line_id = fields.Many2many("sale.order.line", string="Sale Order")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
 

    def create_installment(self):
        if self.sale_order_line_id:
            action = self.env.ref('road_master.device_installation_action').read()[0]
            form_view = [(self.env.ref('road_master.device_installation_form_view').id, 'form')]
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            action['context'] = {'default_sale_order_id': self.sale_order_id.id or False}
            action['context'].update({'default_order_line': self.sale_order_line_id.ids or False})
            return action


