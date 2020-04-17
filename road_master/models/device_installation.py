# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from datetime import datetime


class DeviceInstallation(models.Model):
    _name = "device.installation"
    _inherit = ['mail.thread']
    _description = "Device Installation"
    _order = "id desc"

    name = fields.Char("Name", help="Installation schedule name.")
    user_id = fields.Many2one('res.users', string='Responsible', copy=False, index=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one("res.partner", ondelete="restrict", copy=False, string="Partner", help="Related Partner")
    installation_schedule_date = fields.Date("Installation Schedule Date", copy=False,)
    installation_done_date = fields.Date("Installation Done Date", copy=False)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", ondelete="restrict", copy=False, help="Related Sale Order")
    device_installation_line_ids = fields.One2many("device.installation.line", "device_installation_id",
                                                   string="Device Installation Lines")
    state = fields.Selection([("draft","Draft"),
                              ("confirmed", "Confirmed"),
                              ("received", "Received"),
                              ("done_tests", "Done Tests"),
                              ("installation_in_progress", "Installation In Progress"),
                              ("done_installation", "Done Installation"),
                              ("done", "Done"),
                              ("cancelled", "Cancelled")],
                             string="State", default="draft", copy=False, required=True, tracking=True)
    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)
    mobile_location_id = fields.Many2one("stock.location", string="Mobile Location", default=False, copy=False,
                                         ondelete="restrict", help="Mobile Location for given installation schedule.")

    delivery_count = fields.Integer("Delivery", compute="get_delivery_count", store=False,
                                    help="Delivery count for this device installation.")
    invoice_count = fields.Integer("Invoice", compute="get_invoice_count", store=False,
                                    help="Invoice count for this device installation.")
    subscription_count = fields.Integer("Subscriptions", compute="get_subscriptions_count", store=False,
                                        help="Subscriptions count for this device installation.")

    #Start Installation Fields
    contact_person_id = fields.Many2one("res.partner", string="Contract Person", copy=False, ondelete="restrict", help="Person to contact during installation.")
    contact_no = fields.Char("Contact No.", copy=False)
    installation_location_id = fields.Many2one("res.partner", string="Installation Location", copy=False, ondelete="restrict", help="Location to install devices.")
    manager_user_id = fields.Many2one("res.users", string="Responsible Manager", copy=False, ondelete="restrict", help="Manager responsible for installation process.")
    is_sign = fields.Boolean("Is Sign?")

    #Done Installation Field
    installation_picture_ids = fields.One2many("installation.picture", "device_installation_id", string="Installation Pictures", copy=False, help="Pictures of device installation process.")

    def get_portal_url(self):
        url = '/my/signature/%s'%self.id
        return url

    def get_portal_sign_mail_url(self):
        url = '/my/installation/%s'%self.id
        return url

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'device.installation', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('device.installation', sequence_date=seq_date) or _('New')
        return super(DeviceInstallation, self).create(vals)

    def get_delivery_count(self):
        for record in self:
            record.delivery_count = len(record.device_installation_line_ids.mapped("picking_ids"))

    def get_invoice_count(self):
        invoice_line_obj = self.env["account.move.line"]
        for record in self:
            subscriptions = record.device_installation_line_ids.mapped("subscription_id")
            invoices = invoice_line_obj.search([('subscription_id', 'in', subscriptions.ids)]).mapped("move_id")
            record.invoice_count = len(invoices.ids)

    def get_subscriptions_count(self):
        for record in self:
            record.subscription_count = len(record.device_installation_line_ids.mapped("subscription_id").ids)

    def action_view_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.device_installation_line_ids.mapped("picking_ids")
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

    def action_view_invoices(self):
        invoice_line_obj = self.env["account.move.line"]
        subscriptions = self.device_installation_line_ids.mapped("subscription_id")
        invoices = invoice_line_obj.search([('subscription_id', 'in', subscriptions.ids)]).mapped("move_id")
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.sale_order_id.partner_id.id,
                'default_partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.sale_order_id.payment_term_id.id,
                'default_invoice_origin': self.sale_order_id.mapped('name'),
                'default_user_id': self.sale_order_id.user_id.id,
            })
        action['context'] = context
        return action

    def action_open_subscriptions(self):
        """Display the linked subscription and adapt the view to the number of records to display."""
        self.ensure_one()
        subscriptions = self.device_installation_line_ids.mapped("subscription_id")
        action = self.env.ref('sale_subscription.sale_subscription_action').read()[0]
        if len(subscriptions) > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
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

    @api.model
    def default_get(self, fields):
        device_installation_line_obj = self.env["device.installation.line"]
        defaults = super(DeviceInstallation, self).default_get(fields)
        sale_order = self._context.get("default_sale_order_id", False) and self.env["sale.order"].browse(self._context.get("default_sale_order_id")) or False
        sale_order_line = self._context.get("default_order_line", False) and self.env["sale.order.line"].browse(self._context.get("default_order_line")) or False
        if sale_order:
            defaults['branch_id'] = sale_order.branch_id.id
            installation_lines_data = []
            for line in sale_order_line:
                device_installation_line = sale_order.device_installation_ids.mapped("device_installation_line_ids").filtered(lambda dil: dil.sale_line_id == line)
                move_id = sale_order.picking_ids.mapped("move_line_ids_without_package").filtered(lambda dil: dil.product_id.id == line.product_id.id).sorted(key=lambda r: r.id, reverse=True)
                remaining_qty = line.product_uom_qty or 0
                if device_installation_line and device_installation_line.product_id == line.product_id and device_installation_line.quantity > 0 and line.product_uom_qty > 0:
                    remaining_qty = line.product_uom_qty - device_installation_line.quantity

                if remaining_qty > 0:
                    line_vals = {
                        "product_id": line.product_id.id,
                        "quantity": remaining_qty if remaining_qty > 0 else line.product_uom_qty,
                        "unit_price": line.price_unit,
                        "product_uom_id": line.product_uom.id,
                        "sale_line_id": line.id,
                    }
                    if move_id: 
                        if move_id[0].product_uom_qty > 0 or move_id[0].qty_done > 0:
                            line_vals.update({'lot_id': move_id[0].lot_id.id or False})
                    line_vals and installation_lines_data.append((0, 0, line_vals))
            if installation_lines_data:
                defaults["device_installation_line_ids"] = installation_lines_data
            defaults["partner_id"] = sale_order.partner_id.id

            location_domain = [
                ('branch_id', '=', sale_order.branch_id.id),
                ('company_id', '=', sale_order.company_id.id),
                ('mobile_location', '=', True)
            ]
            location = self.env["stock.location"].search(location_domain, limit=1)
            defaults["mobile_location_id"] = location.id
        defaults["installation_schedule_date"] = datetime.now().date()

        return defaults

    def action_confirm(self):
        if not self.device_installation_line_ids:
            raise Warning(_("You can not confirm Device Installation without lines."))
        self.create_pickings()
        self.write({"state": "confirmed"})
        return True

    def action_received(self):
        for record in self:
            internal_done_pickings = len(record.device_installation_line_ids.mapped("picking_ids").filtered(
                lambda picking: picking.state == 'done' and picking.picking_type_code == 'internal'))
            internal_all_pickings = len(record.device_installation_line_ids.mapped("picking_ids").filtered(
                lambda picking: picking.picking_type_code == "internal"))
            record.device_installation_line_ids.mapped("picking_ids") and record.device_installation_line_ids.mapped("picking_ids").action_done()
            if internal_done_pickings != internal_all_pickings:
                raise Warning(_("All Pickings For Mobile Warehouse Are Not Transferred"))
        self.write({"state": "received"})
        return True

    def action_done_tests(self):
        for line in self.device_installation_line_ids:
            if not line.sim_card_id:
                raise Warning(_("Add SIM Card for device %s in device installation : %s" % (line.product_id.display_name, self.name)))
        self.write({"state": "done_tests"})
        return True

    def action_installation_start(self):
        for line in self.device_installation_line_ids:
            line.is_installation = True
        self.write({"state": "installation_in_progress"})
        return True

    def action_installation_done(self):
        for record in self:
            if not record.installation_picture_ids:
                raise Warning(_("""Installation Pictures are not uploaded in installation process %s. Please upload images of installed device.""" % record.display_name))
            for line in record.device_installation_line_ids:
                if not line.vehicle_plate_no:
                    raise Warning(_("""Vehicle Plate No is not updated in installation process %s. Please update Vehicle Plate No of installed device.""" % line.product_id.display_name))
        self.write({"state": "done_installation"})
        return True

    def action_done(self):
        if self.state != 'done_installation':
            raise Warning(_("You can process installation to 'Done' state only after completing done installation process with installation images."))
        ctx = dict(self._context)
        ctx.update({'device_install_process': True})

        for record in self:
            record.with_context(ctx).create_installation_subscription()

        self.write({"state": "done"})
        for order in self.mapped("sale_order_id"):
            if len(order.mapped("device_installation_ids")) == len(order.mapped("device_installation_ids").filtered(lambda di: di.state == "done")):
                order.with_context(ctx).action_confirm()
            # order.mapped("order_line")._compute_qty_delivered()

        return True

    def check_installation_done_constrains(self):
        for record in self:
            outgoing_done_pickings = len(record.device_installation_line_ids.mapped("picking_ids").filtered(
                lambda picking: picking.state == 'done' and picking.picking_type_code == 'outgoing'))
            outgoing_all_pickings = len(record.device_installation_line_ids.mapped("picking_ids").filtered(
                lambda picking: picking.picking_type_code == "outgoing"))
            record.device_installation_line_ids.mapped("picking_ids") and record.device_installation_line_ids.mapped("picking_ids").action_done()
            if outgoing_done_pickings != outgoing_all_pickings:
                raise Warning(_("All Pickings For Customer Delivery Are Not Transferred"))

            if not record.installation_done_date:
                raise Warning(_("Update Installation Done Date for Delivery Installation."))

            for line in record.device_installation_line_ids:
                if not line.vehicle_plate_no:
                    raise Warning(_("Update Vehicle Plate No. for device %s in device installation : %s" % (line.product_id.display_name, record.name)))

                if not line.sim_card_id:
                    raise Warning(_("Add SIM Card for device %s in device installation : %s" % (line.product_id.display_name, record.name)))

    def open_signature_url(self):
        self.check_installation_done_constrains()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_sign_mail_url(),
        }

    def send_signature_url(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.check_installation_done_constrains()
        self.ensure_one()
        template_id = self.env.ref("road_master.email_template_installation_signature_url").id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'device.installation', self.ids[0])
        ctx = {
            'default_model': 'device.installation',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def create_installation_subscription(self):
        sale_subscription_obj = self.env["sale.subscription"]
        sale_subscription_line_obj = self.env["sale.subscription.line"]
        subscription_fields = sale_subscription_obj.fields_get()
        vals = sale_subscription_obj.default_get(subscription_fields)
        vals.update({
            "partner_id": self.partner_id.id,
        })
        temp_rec = sale_subscription_obj.new(vals)
        temp_rec.onchange_partner_id()
        temp_rec.onchange_user_id()
        temp_rec.onchange_date_start()
        temp_rec.on_change_template()
        subscription_vals = temp_rec._convert_to_write(temp_rec._cache)
        subscription_line_data = []
        for line in self.device_installation_line_ids:
            subscription_line_fields = sale_subscription_line_obj.fields_get()
            line_vals = sale_subscription_line_obj.default_get(subscription_line_fields)
            line_vals.update({
                "product_id": line.product_id.id,
                "quantity": line.quantity,
            })
            temp_line_rec = sale_subscription_line_obj.new(line_vals)
            temp_line_rec.onchange_product_id()
            temp_line_rec.onchange_product_quantity()
            temp_line_rec.onchange_uom_id()
            subscription_line_vals = temp_line_rec._convert_to_write(temp_line_rec._cache)
            subscription_line_vals.update({"price_unit": line.unit_price})
            subscription_line_data.append((0, 0, subscription_line_vals))
        subscription_vals.update({
            "recurring_invoice_line_ids": subscription_line_data,
        })
        if self.sale_order_id and self.sale_order_id.subscription_renew_type:
            subscription_vals.update({
                "to_renew": True,
                "renew_type": self.sale_order_id.subscription_renew_type
            })
        new_subscription = sale_subscription_obj.create(subscription_vals)
        self.device_installation_line_ids.write({"subscription_id": new_subscription.id if new_subscription else False})
        new_subscription.recurring_invoice()
        all_subscriptions = self.sale_order_id.device_installation_ids.mapped("device_installation_line_ids").mapped("subscription_id").filtered(lambda sub: sub.renew_type == 'based_on_last_plate_expiry_date')
        if all_subscriptions:
            last_plate_recurring_nextdate = max(all_subscriptions.mapped('recurring_next_date'))
            subscription_write_vals = {"recurring_next_date": last_plate_recurring_nextdate}

            last_plate_date = max(all_subscriptions.mapped('date')) or False
            if last_plate_date:
                subscription_write_vals.update({"date": last_plate_date})

            all_subscriptions.write(subscription_write_vals)

    def action_cancel(self):
        self.write({"state": "cancelled"})
        return True

    def create_procurement_group(self):
        procurement_group_obj = self.env["procurement.group"]
        procurement_group_fields = procurement_group_obj.fields_get()
        procurement_group_vals = procurement_group_obj.default_get(procurement_group_fields)
        procurement_group_vals.update({"partner_id": self.partner_id.id})
        procurement_group = procurement_group_obj.create(procurement_group_vals)
        return procurement_group

    def create_pickings(self):
        stock_picking_obj = self.env["stock.picking"]
        stock_picking_type_obj = self.env["stock.picking.type"]
        stock_location_obj = self.env["stock.location"]
        stock_move_obj = self.env["stock.move"]
        picking_fields = stock_picking_obj.fields_get()
        for device_installation in self:
            for line in device_installation.device_installation_line_ids:
                procurement_group = self.create_procurement_group()
                picking_data = stock_picking_obj.default_get(picking_fields)
                internal_picking_type = device_installation.sale_order_id.warehouse_id.int_type_id
                out_picking_type = device_installation.sale_order_id.warehouse_id.out_type_id

                tmp_stock_move = stock_move_obj.new({
                    "product_id": line.product_id.id,
                    "product_uom_qty": line.quantity
                })
                tmp_stock_move.onchange_product()
                tmp_stock_move.onchange_quantity()
                stock_move_vals = tmp_stock_move._convert_to_write(tmp_stock_move._cache)
                if 'product_qty' in list(stock_move_vals.keys()):
                    stock_move_vals.pop('product_qty')

                transit_location = device_installation.mobile_location_id

                # Internal Picking (Stock -> Mobile Warehouse)

                int_picking_data = picking_data
                int_picking_data.update({
                    "picking_type_id": internal_picking_type.id,
                    "device_installtion_line_id": line.id,
                })
                temp_picking = stock_picking_obj.new(int_picking_data)
                temp_picking.onchange_picking_type()
                int_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
                internal_move_vals = stock_move_vals
                internal_move_vals.update({
                    'name': line.product_id.description or line.product_id.display_name,
                    'product_uom': line.product_uom_id.id,
                    'group_id': procurement_group.id,
                })
                int_picking_vals.update({
                    'location_dest_id': transit_location.id,
                    'move_ids_without_package': [(0, 0, internal_move_vals)],
                    # 'group_id': procurement_group.id,
                })
                internal_picking = stock_picking_obj.create(int_picking_vals)
                if internal_picking.state == 'draft':
                    internal_picking.action_confirm()
                if internal_picking.state in ['confirmed', 'waiting']:
                    internal_picking.action_assign()

                # Outgoing Picking (Mobile Warehouse -> Customer)

                out_picking_data = picking_data
                out_picking_data.update({
                    "picking_type_id": out_picking_type.id,
                    "device_installtion_line_id": line.id,
                })
                temp_picking = stock_picking_obj.new(int_picking_data)
                temp_picking.onchange_picking_type()
                out_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
                out_move_vals = stock_move_vals
                out_move_vals.update({
                    'name': line.product_id.description or line.product_id.display_name,
                    'product_uom': line.product_uom_id.id,
                    'group_id': procurement_group.id,
                })
                out_picking_vals.update({
                    'location_id': transit_location.id,
                    'move_ids_without_package': [(0, 0, stock_move_vals)],
                    # 'group_id': procurement_group.id,
                })
                out_picking = stock_picking_obj.create(out_picking_vals)
                if out_picking.state == 'draft':
                    out_picking.action_confirm()
                if out_picking.state in ['confirmed', 'waiting']:
                    out_picking.action_assign()

        return True


class DeviceInstallationLine(models.Model):
    _name = "device.installation.line"
    _description = "Device Installation Line"
    _order = "id"
    _rec_name = "device_installation_id"

    device_installation_id = fields.Many2one("device.installation", string="Device Installation Ref.",
                                             copy=False, ondelete="cascade", help="Related Device Installation.")
    vehicle_plate_no = fields.Char("Vehicle Plate No.", copy=False)
    product_id = fields.Many2one("product.product", string="Product", copy=False, help="Select Device For Installation")
    quantity = fields.Float("Quantity", help="Quantity to be installed.")
    unit_price = fields.Float("Unit Price")
    lot_id = fields.Many2one("stock.production.lot", string="Serial No", help="Related Lot / Serial No.")
    installation_picture = fields.Binary('Installation Picture')
    is_installation = fields.Boolean("Is Installation", default=False)
    product_uom_id = fields.Many2one("uom.uom", copy=False, ondelete="restrict", string="Unit of Measure")
    sale_order_id = fields.Many2one("sale.order", string="Sale Order", copy=False, ondelete="restrict", help="Related Sale Order")
    sim_card_id = fields.Many2one("sim.card", string="Sim Card", copy=False, ondelete="restrict")
    picking_ids = fields.One2many("stock.picking", "device_installtion_line_id", string="Picking", copy=False, help="Related Stock Picking.")
    invoice_id = fields.Many2one("account.move", string="Invoices", copy=False, ondelete="restrict", help="Related Invoices.")
    sub_total = fields.Float("Subtotal", compute="get_sub_total", store=True, help="Total amount for device installation line.")
    sale_line_id = fields.Many2one("sale.order.line", string="Sale Order Line", copy=False, ondelete="restrict", help="Related Sale Order Line.")
    subscription_id = fields.Many2one("sale.subscription", string="Subscription", copy=False, ondelete="restrict", help="Related Sunscriptions.")

    @api.depends("quantity", "unit_price")
    def get_sub_total(self):
        for record in self:
            record.sub_total = record.quantity * record.unit_price


class installtion_picture(models.Model):
    _name = "installation.picture"
    _description = "Installation Picture"
    _order = "id desc"

    name = fields.Char("Title", help="Title for image.")
    image = fields.Binary("Image", required=True, copy=False, help="Installation Process Image.")
    device_installation_id = fields.Many2one("device.installation", string="Device Installation",
                                             copy=False, ondelete="restrict", help="Device Installation Ref.")
