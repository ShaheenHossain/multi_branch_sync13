# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models
from odoo.tools.float_utils import float_round as round
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    warranty_details = fields.One2many('warranty.detail', 'sale_id', string="Warranty Info")

    def action_add_sales_warranty(self):
        """
            Method for add sales warranty in order.
        """
        self.ensure_one()
        current_date = fields.Datetime.now()
        for line in self.order_line.filtered(lambda l: l.product_id.tracking == 'serial'):
            if line.product_id.warranty_id and not self.warranty_details:
                warranty_term_months = line.product_id.warranty_id.warranty_months or 0
                end_date = current_date + relativedelta(months=warranty_term_months)
                for qty in range(int(round(line.product_uom_qty,0))):
                    move_line_ids = self.picking_ids.mapped("move_line_ids").filtered(lambda sml: sml.product_id == line.product_id and sml.product_uom_qty > 0 or sml.qty_done > 0)
                    serial_id = move_line_ids and move_line_ids[0].lot_id or False
                    warranty_vals = {
                        'sale_id': line.order_id.id,
                        'sale_line_id': line.id,
                        'product_id': line.product_id.id,
                        'template_id': line.product_id.warranty_id.id,
                        'partner_id': line.order_id.partner_id.id,
                        'partner_phone': line.order_id.partner_id.phone,
                        'partner_email': line.order_id.partner_id.email,
                        'user_id': line.order_id.user_id.id or self.env.user.id,
                        'warranty_info': line.product_id.warranty_id.warranty_info,
                        'warranty_tc': line.product_id.warranty_id.warranty_tc,
                        'tag_ids': [(6, 0, line.order_id.tag_ids.ids)],
                        'warranty_cost': line.product_id.warranty_id.warranty_cost or 0.0,
                        'start_date': current_date,
                        'end_date': end_date,
                    }
                    serial_id and warranty_vals.update({"serial_id": serial_id.id})
                    warranty = self.env['warranty.detail'].create(warranty_vals)
                    return warranty

    # def action_confirm(self):
    #     """
    #         Override method for create warranty records
    #     """
    #     res = super(SaleOrder, self).action_confirm()
    #     context = dict(self.env.context)
    #     if not context.get('from_repair'):
    #         for line in self.order_line.filtered(lambda l: l.product_id.tracking == 'serial'):
    #             if line.product_id.warranty_id:
    #                 for qty in range(int(round(line.product_uom_qty,0))):
    #                     warranty_id = self.env['warranty.detail'].create({
    #                             'sale_id': line.order_id.id,
    #                             'sale_line_id': line.id,
    #                             'product_id': line.product_id.id,
    #                             'template_id': line.product_id.warranty_id.id,
    #                             'partner_id': line.order_id.partner_id.id,
    #                             'partner_phone': line.order_id.partner_id.phone,
    #                             'partner_email': line.order_id.partner_id.email,
    #                             'user_id': line.order_id.user_id.id or self.env.user.id,
    #                             'warranty_info': line.product_id.warranty_id.warranty_info,
    #                             'warranty_tc': line.product_id.warranty_id.warranty_tc,
    #                             'tag_ids': [(6, 0, line.order_id.tag_ids.ids)],
    #                         })
    #                     warranty_id.action_pending()
    #     return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warranty_details = fields.One2many('warranty.detail', 'sale_line_id', string="Warranty Info")
