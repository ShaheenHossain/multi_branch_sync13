# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ChangeProductWizard(models.TransientModel):
    _name = "change.product.wizard"
    _description = "Change Product Wizard"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product")
    change_product_line_ids = fields.One2many("change.product.line", "change_product_wizard_id", string="Change Product Lines")

    def get_product_qty(self, product, warehouse):
        ctx = dict(self._context)
        ctx.update({"warehouse": warehouse.id})
        products = product.filtered(lambda p: p.type != 'service')
        res = products.with_context(ctx)._compute_quantities_dict(self._context.get('lot_id'),
                                                                  self._context.get('owner_id'),
                                                                  self._context.get('package_id'),
                                                                  self._context.get('from_date'),
                                                                  self._context.get('to_date'))
        qty = res.get(product.id, {}).get('qty_available', 0.0)
        return qty

    @api.model
    def default_get(self, fields):
        product_obj = self.env["product.product"]
        ctx = dict(self._context)
        result = super(ChangeProductWizard, self).default_get(fields)
        if not self._context.get('active_id', False):
            return result
        replace_lines_data = []
        user_warehouses = self.env["stock.warehouse"].search([('branch_id', 'in', self.env.user.branch_ids.ids)])
        line = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        for similar_product in line.product_id.product_tmpl_id.similar_product_ids:
            line_qty = 0.0
            if self._context.get("active_model") == "helpdesk.workorder":
                line_qty = line.quantity
            else:
                line_qty = line.product_uom_qty
            for warehouse in user_warehouses:
                product_quantity = self.get_product_qty(similar_product, warehouse)
                similar_product_price_unit = similar_product.uom_id._compute_price(similar_product.lst_price, similar_product.uom_id)
                if product_quantity >= line_qty:
                    replace_lines_data.append([0, 0, {
                        "change": False,
                        "product_id": similar_product.id,
                        "warehouse_id": warehouse.id,
                        "quantity": product_quantity,
                        "price": similar_product_price_unit
                    }])
        if replace_lines_data:
            result["change_product_line_ids"] = replace_lines_data
        return result

    def process_replace_product(self):
        if not self.change_product_line_ids.filtered(lambda line : line.change):
            raise Warning(_("You have not selected any product to replace sale order product."))

        if len(self.change_product_line_ids.filtered(lambda line : line.change)) > 1:
            raise Warning(_("You can select only 1 product to replace sale order product."))

        if len(self.change_product_line_ids.filtered(lambda line: line.change)) == 1:
            replace_product_line = self.change_product_line_ids.filtered(lambda line: line.change)
            line = self.env[self._context.get("active_model")].browse(self._context.get('active_id'))
            line.product_id = replace_product_line.product_id
            if self._context.get("active_model") == "sale.order.line":
                line_qty = line.product_uom_qty
                line.product_id_change()
                line.product_uom_qty = line_qty
            else:
                line_qty = line.quantity
                line.product_id_onchange()
                line.quantity = line_qty
        return True


class ChangeProductLine(models.TransientModel):
    _name = "change.product.line"
    _description = "Change Product Line"
    _rec_name = "product_id"

    product_id = fields.Many2one("product.product", string="Product", help="Similar Product To Replace.")
    change = fields.Boolean("Change Product")
    quantity = fields.Float("Quantity", help="Available Quantity")
    price = fields.Float("Price", help="Current Unit Price")
    change_product_wizard_id = fields.Many2one("change.product.wizard", string="Change Product Wizard")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", help="Related Warehouse")
