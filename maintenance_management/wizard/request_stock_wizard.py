# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RequestStockWizard(models.TransientModel):
    _name = "request.stock.wizard"
    _description = "Request Stock Wizard"

    request_stock_lines = fields.One2many("request.stock.wizard.line", "request_stock_wizard_id", "Request Stock Lines")

    @api.model
    def default_get(self, fields):
        ctx = dict(self._context)
        result = super(RequestStockWizard, self).default_get(fields)
        if not self._context.get('active_id', False):
            return result
        request_lines_data = []
        picking = self.env["stock.picking"].browse(self._context.get('active_id'))
        warehouse_ids = self.env["stock.warehouse"].search([('branch_id', '=', picking.branch_id.id), ('id', '!=', picking.sale_id.warehouse_id.id)])
        for line in picking.move_ids_without_package:
            if (line.reserved_availability + line.quantity_done) >= line.product_uom_qty:
                continue
            for warehouse in warehouse_ids:
                ctx.update({"warehouse": warehouse.id})
                product_quantity = line.product_id.with_context(ctx).qty_available
                if product_quantity > 0.0:
                    request_lines_data.append([0, 0, {
                        "product_id": line.product_id.id,
                        "warehouse_id": warehouse.id,
                        "quantity": product_quantity,
                        "picking_id": picking.id
                    }])
        if request_lines_data:
            result["request_stock_lines"] = request_lines_data
        return result

    def create_request(self):
        stock_picking_obj = self.env["stock.picking"]
        stock_move_obj = self.env["stock.move"]
        for line in self.request_stock_lines:
            if line.request and line.request_qty > 0.0:
                picking_fields = stock_picking_obj.fields_get()
                picking_data = stock_picking_obj.default_get(picking_fields)
                internal_picking_type = line.warehouse_id.int_type_id

                tmp_stock_move = stock_move_obj.new({
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.request_qty,
                    "product_uom": line.product_id.uom_id.id
                })
                tmp_stock_move.onchange_product()
                tmp_stock_move.onchange_quantity()
                stock_move_vals = tmp_stock_move._convert_to_write(tmp_stock_move._cache)
                if 'product_qty' in list(stock_move_vals.keys()):
                    stock_move_vals.pop('product_qty')

                int_picking_data = picking_data
                int_picking_data.update({
                    "picking_type_id": internal_picking_type.id,
                })
                temp_picking = stock_picking_obj.new(int_picking_data)
                temp_picking.onchange_picking_type()
                int_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
                internal_move_vals = stock_move_vals
                internal_move_vals.update({
                    'name': line.product_id.description or line.product_id.display_name,
                })
                int_picking_vals.update({
                    'location_dest_id': line.picking_id.location_id.id,
                    'move_ids_without_package': [(0, 0, internal_move_vals)],
                })
                internal_picking = stock_picking_obj.create(int_picking_vals)
                internal_picking.picking_id = line.picking_id.id
                if internal_picking.state == 'draft':
                    internal_picking.action_confirm()
                if internal_picking.state in ['confirmed', 'waiting']:
                    internal_picking.action_assign()


class RequestStockWizardLine(models.TransientModel):
    _name = "request.stock.wizard.line"
    _description = "Request Stock Wizard line"
    _rec_name = "product_id"

    request_stock_wizard_id = fields.Many2one("request.stock.wizard", string="Request Stock Wizard")
    request = fields.Boolean("Request", help="Select to request product stock from warehouse.")
    product_id = fields.Many2one("product.product", string="Product", help="Product Reference.")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse")
    quantity = fields.Float("Quantity Available")
    request_qty = fields.Float("Request Quantity")
    picking_id = fields.Many2one("stock.picking", string="Picking", help="Related Picking")
