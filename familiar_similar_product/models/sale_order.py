# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_out_of_stock = fields.Boolean("Out Of Stock", compute="get_is_out_of_stock", store=False)

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id")
    def get_is_out_of_stock(self):
        ctx = dict(self._context)
        for line in self:
            line.is_out_of_stock = False
            if not line.product_id:
                continue
            ctx.update({"warehouse": line.order_id.warehouse_id.id})
            product = line.product_id.with_context(ctx)
            existing_stock = product.qty_available
            if existing_stock < line.product_uom_qty:
                line.is_out_of_stock = True
