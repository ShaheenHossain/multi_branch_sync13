# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning
from odoo.tools import float_is_zero
from itertools import groupby


class SaleOrder(models.Model):
    _inherit = "sale.order"

    rmts_device_installation = fields.Boolean("RMTS Device Installation", compute="get_rmts_device", store=False,
                                              help="Manage RMTS Device Insallation orders separately using this checkbox.")
    device_installation_ids = fields.One2many("device.installation", "sale_order_id", string="Device Installations",
                                              copy=False, help="Related Device Installations")
    installation_count = fields.Integer("Installation Schedules", compute="get_installation_count", store=False)
    subscription_renew_type = fields.Selection([("based_on_plate_expory_date", "Based On Plate Expiry Date"),
                                                ("based_on_last_plate_expiry_date", "Based On Last Plate Expiry Date")],
                                               string="Renew Type", copy=False, help="Renew type based on plates.")

    def _compute_subscription_count(self):
        super(SaleOrder, self)._compute_subscription_count()
        if self.rmts_device_installation:
            for order in self:
                order.subscription_count = len(order.device_installation_ids.mapped("device_installation_line_ids").mapped("subscription_id").ids)

    def action_open_subscriptions(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        if self.rmts_device_installation:
            subscriptions = self.device_installation_ids.mapped("device_installation_line_ids").mapped("subscription_id")
            action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
            if len(subscriptions) > 1:
                action['domain'] = [('id', 'in', subscriptions.ids)]
                # tree_view = [(self.env.ref('sale_subscription.sale_subscription_view_list').id, 'tree')]
                # if 'views' in action:
                #     action['views'] = tree_view + [(state, view) for state, view in action['views'] if view != 'form']
                # else:
                #     action['views'] = tree_view
                # action['res_id'] = subscriptions.ids[0]
            elif len(subscriptions) == 1:
                form_view = [(self.env.ref('sale_subscription.sale_subscription_view_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = subscriptions.ids[0]
            else:
                action = {'type': 'ir.actions.act_window_close'}
            action['context'] = dict(self._context, create=False)
            return action
        return super(SaleOrder, self).action_open_subscriptions()

    @api.depends("order_line", "order_line.product_id")
    def get_rmts_device(self):
        for record in self:
            is_rmts_device = False
            if True in record.order_line.mapped("product_id").mapped("product_tmpl_id").mapped("is_rmts_device"):
                is_rmts_device = True
            record.rmts_device_installation = is_rmts_device

    def get_installation_count(self):
        for order in self:
            order.installation_count = len(order.device_installation_ids.ids)

    def create_installment_schedule(self):
        installation_id = []
        if not self.mapped("order_line").filtered(lambda line: line.product_id and line.product_id.product_tmpl_id.is_rmts_device):
            raise Warning(_("There is No RMTS Device Product in order line. You can not create device installation."))
        for order_line in self.order_line:
            if self.device_installation_ids and order_line.id not in self.device_installation_ids.mapped('device_installation_line_ids').sale_line_id.ids:
                installation_id.append(order_line) 
        if not self.device_installation_ids:
            installation_id = self.order_line
        if installation_id:
            ctx = {
                'default_sale_order_id': self.id,
                'default_sale_order_line_id': [(4, sale_id.id) for sale_id in installation_id],
            }
            return {
                'name':_("Sale Order Line"),
                'view_mode': 'form',
                'view_id': self.env.ref('road_master.installation_product_selection_wizard_form').id,
                'view_type': 'form',
                'res_model': 'installation.product.selection',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': ctx,
                }
        else:
            raise Warning(_("You have already created installation schedule for this sale order"))

    def action_view_installment_schedules(self):
        device_installation_ids = self.mapped('device_installation_ids')
        action = self.env.ref('road_master.device_installation_action').read()[0]
        if len(device_installation_ids) > 1:
            action['domain'] = [('id', 'in', device_installation_ids.ids)]
        elif len(device_installation_ids) == 1:
            form_view = [(self.env.ref('road_master.device_installation_form_view').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = device_installation_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _split_subscription_lines(self):
        """Split the order line according to subscription templates that must be created."""
        self.ensure_one()
        res={}
        if not self.rmts_device_installation:
            res = super(SaleOrder, self)._split_subscription_lines()
        else:
            res = dict()
            sale_line_ids = self.env["device.installation.line"].search([('sale_line_id','in',self.order_line.ids),('device_installation_id.state','=','done')]).mapped("sale_line_id")
            new_sub_lines = self.order_line.filtered(lambda l: not l.subscription_id and l.product_id.subscription_template_id and l.product_id.recurring_invoice and l.id in sale_line_ids.ids)
            templates = new_sub_lines.mapped('product_id').mapped('subscription_template_id')
            for template in templates:
                lines = self.order_line.filtered(lambda l: l.product_id.subscription_template_id == template)
                res[template] = lines

        return res

    def create_subscriptions(self):
        res = []
        if not self.rmts_device_installation or self._context.get("device_install_process", False):
            res = super(SaleOrder, self).create_subscriptions()
        return res


    def action_confirm(self):
        for order in self:
            if not self._context.get("device_install_process", False):
                for device_installation in order.device_installation_ids:
                    if device_installation.state != "done":
                        message="You can not confirm RMTS Installation order if installation schedule process is not Completed.Device Installation Record %s is not in done state." % device_installation.display_name
                        raise Warning(_(message))
        return super(SaleOrder, self).action_confirm()

    def _create_invoices(self, grouped=False, final=False):
        """
        Process changes for invoice creation of RMTS Installation devices.
        For Non RMTS Device Orders, Process will work nornally.
        """
        if not self.rmts_device_installation:
            return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.device_installation_ids.mapped("device_installation_line_ids").filtered(lambda dil: dil.device_installation_id.state == "done").mapped("sale_line_id"):
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (x.get('partner_id'), x.get('currency_id'))):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs),
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Manage 'final' parameter: transform out_invoice to out_refund if negative.
        out_invoice_vals_list = []
        refund_invoice_vals_list = []
        if final:
            for invoice_vals in invoice_vals_list:
                if sum(l[2]['quantity'] * l[2]['price_unit'] for l in invoice_vals['invoice_line_ids']) < 0:
                    for l in invoice_vals['invoice_line_ids']:
                        l[2]['quantity'] = -l[2]['quantity']
                    invoice_vals['type'] = 'out_refund'
                    refund_invoice_vals_list.append(invoice_vals)
                else:
                    out_invoice_vals_list.append(invoice_vals)
        else:
            out_invoice_vals_list = invoice_vals_list

        # Create invoices.
        moves = self.env['account.move'].with_context(default_type='out_invoice').create(out_invoice_vals_list)
        moves += self.env['account.move'].with_context(default_type='out_refund').create(refund_invoice_vals_list)
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves
