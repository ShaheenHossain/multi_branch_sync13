# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class RequestJobCardDataWizard(models.TransientModel):
    _name = "request.job.card.data.wizard"
    _description = "Request Job Card Wizard"

    lot_id = fields.Many2one("stock.production.lot", string="Serial No", help="Related Lot / Serial No.")
    serial_no = fields.Char(string="Serial No", help="Related Lot / Serial No.", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer", help="Related Customer")
    sale_order_id = fields.Many2many("sale.order", string="Sale Order")
    warranty_id = fields.Many2many("warranty.detail", help="Related Warranty")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")   
    job_card_id = fields.Many2many('helpdesk.ticket', string="Job Card") 

    def get_job_card_data(self):
        if self.serial_no:
            self.lot_id = self.env["stock.production.lot"].search([('name', '=', self.serial_no)])
            stock_picking_id = self.env["stock.picking"].search([('move_line_ids_without_package.lot_id', '=', self.lot_id.id)])
            job_card_id = self.env["helpdesk.ticket"].search([('lot_id', '=', self.lot_id.id)])
            sale_order_id = self.env["sale.order"].search([('picking_ids.id', 'in', stock_picking_id.ids)], order="id desc")
            warranty_id = self.env["warranty.detail"].search([('sale_id', 'in', sale_order_id.ids or False)])
            if sale_order_id and not sale_order_id[0].partner_id.is_distributor:
                ctx = {
                    'default_partner_id': sale_order_id and sale_order_id[0].partner_id.id,
                    'default_sale_order_id': [(4, sale_id.id) for sale_id in sale_order_id],
                    'default_warehouse_id': sale_order_id and sale_order_id[0].warehouse_id.id,
                    'default_warranty_id': [(4, warranty.id) for warranty in warranty_id],
                    'default_job_card_id': [(4, job_card.id) for job_card in job_card_id],
                    'default_serial_no': self.serial_no,
                }
                return {
                    'name':_("Sale Order Data"),
                    'view_mode': 'form',
                    'view_id': self.env.ref('maintenance_management.request_job_card_show_wizard_form').id,
                    'view_type': 'form',
                    'res_model': 'request.job.card.data.wizard',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'context': ctx
                }
            else:
                raise Warning('No ralated data found for %s'% self.lot_id.name)

