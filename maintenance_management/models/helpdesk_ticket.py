# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
import logging
import datetime
_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def _default_warehouse_id(self):
        company = self.env.company.id
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        return warehouse_ids

    @api.model
    def default_get(self, fields):
        result = super(HelpdeskTicket, self).default_get(fields)
        if result.get('team_id') and fields:
            result['team_id'] = self.get_defaut_team(result.get('is_job_card', False))
        return result

    def get_defaut_team(self, is_job_card):
        helpdesk_team_obj = self.env["helpdesk.team"]
        if is_job_card:
            team_id = helpdesk_team_obj.search([('member_ids', 'in', self.env.uid), ('is_jobcard_team', '=', True)], limit=1, order='id').id
            if not team_id:
                team_id = helpdesk_team_obj.search([('is_jobcard_team', '=', True)], limit=1, order='id').id
        else:
            team_id = helpdesk_team_obj.search([('member_ids', 'in', self.env.uid), ('is_jobcard_team', '!=', True)], limit=1, order='id').id
            if not team_id:
                team_id = helpdesk_team_obj.search([('is_jobcard_team', '!=', True)], limit=1, order='id').id
        return team_id

    #Job Card Fields
    sequence = fields.Char(string='Sequence', help="Sequence", default=lambda self: _('New'))
    is_job_card = fields.Boolean("Job Card", default=False, help="Is this helpdesk ticket a job card?")
    is_paper_based_jc = fields.Boolean("Paper Based Job Card", default=False, help="Check if paper based jobcard.")
    jobcard_file = fields.Binary("Job Card File", help="Job card document for paper based job card.")
    jobcard_reference = fields.Char("Reference", help="Paper Based Job Card Reference.")
    is_create_quotation = fields.Boolean("Create Quotation", related="stage_id.is_create_quotation",default=False, help="Allow Create Quotation in this ticket.")
    is_request_spare_parts = fields.Boolean("Request Spare Parts", related="stage_id.is_request_spare_parts", default=False, help="Allow Request Spare Parts in this ticket.")
    is_return_and_refund = fields.Boolean("Return And Refund Device", related="stage_id.is_return_and_refund", help="Allow Return And Refung device in this ticket.")
    is_replace_and_invoice = fields.Boolean("Replace And Generate Invoice", related="stage_id.is_replace_and_invoice", help="Allow replace and invoice generation in this stage.")
    jobcard_date = fields.Date("Date", default=fields.Datetime.today(), help="Job Card Creation Date")
    device_category_id = fields.Many2one("product.category", string="Device Category", help="Related Hardware Type")
    warranty_type = fields.Selection([('free_service', 'Free Service'),
                                      ('out_of_warranty', 'Out Of Warranty')], default='free_service')
    warranty_approval_type = fields.Selection([('invoice', 'Invoice'),
                                               ('warranty_card', 'Warranty Card'),
                                               ('warranty_card_and_invoice', 'Warranty Card + Invoice'),
                                               ('manager_approval', 'Manager Approval')],
                                              string="Warranty Approval Type", default='invoice', required=True)
    warranty_approval_manager_id = fields.Many2one("res.users", "Warranty Approval Manager", help="If warranty approved by manager, Refer to the manager.")
    warranty_document = fields.Binary("Warranty Document", help="Proof of item warranty to claim free service.")
    branch_id = fields.Many2one("res.branch", default=lambda self: self.env.user.branch_id, help="Related Branch.")
    product_id = fields.Many2one("product.product", string="Product")
    item_code = fields.Char("Item Code")
    item_description = fields.Char("Item Description")
    lot_id = fields.Many2one("stock.production.lot", string="Serial No", help="Related Lot / Serial No.")
    ref_no = fields.Char("Reference No")
    duration_month = fields.Integer("Month(s)")
    duration_year = fields.Integer("Year(s)")
    partner_contact = fields.Integer("Customer Contact")
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", default=_default_warehouse_id)
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    sale_order_line_id = fields.Many2one("sale.order.line", string="Sale Order Line")
    replacement_product_id = fields.Many2one("product.product", string="Replacement Product", help="Product to replace damaged product.")
    discount_product_id = fields.Many2one("product.product", string="Discount Product", help="Discount Product.")
    can_be_repaired = fields.Boolean("Can Be Repaired?", default=False, help="Check if device can be repaired or not.")
    is_distributor_jobcard = fields.Boolean("Distributor Job Card", default=False, help="Is this job card created for distributor?")
    distributor_id = fields.Many2one("res.partner", string="Distributor", help="Distributor for jobcard.")
    invoice_partner = fields.Selection([('distributor', 'Distributor'),
                                        ('customer', 'Customer')], default='distributor',
                                       help="Invoice Partner for Job Card.")
    is_private_jc = fields.Boolean("Provate Job Card", default=False)
    replacement_return_picking_id = fields.Many2one("stock.picking", "Replacement Return Picking", copy=False)
    replacement_picking_id = fields.Many2one("stock.picking", "Replacement Picking", copy=False)
    return_to_scrap_picking_id = fields.Many2one("stock.picking", "Return To Scrap Picking", copy=False)
    replacement_refund_invoice_id = fields.Many2one("account.move", "Replacement Refund Invoice", copy=False)
    replacement_invoice_id = fields.Many2one("account.move", "Replacement Invoice", copy=False)
    # warranty_id = fields.Many2one("warranty.detail", string="Warranty Card", copy=False, help="Related Warranty Card")
    # invoice_id = fields.Many2one("account.move", string="Invoice", copy=False, help="Related Invoice")
    warranty_attachment = fields.Binary("Warranty Card", help="Related Warranty Card")
    invoice_attachment = fields.Binary("Invoice", help="Related Invoice")
    warranty_end_date = fields.Date("Warranty End Date", copy=False, help="Related Warranty End Date")
    engineer_remarks = fields.Text("Engineer Remarks")

    #Customer Complaints
    complaint_description = fields.Text("Complaint Description")
    is_other = fields.Boolean("Other?", default=False)
    customer_complaints_id = fields.Many2many('customer.complaints', "helpdesk_ticket_complaints_rel", string="Customer Complaints", help="Complaints for products." )


    #Work Order Details (Table Needed For Spareparts
    workorder_lines = fields.One2many("helpdesk.workorder", "helpdesk_ticket_id", string="Workorder Lines")

    job_card_type = fields.Selection([("repair", "Repair"),
                                      ("replace", "Replace"),
                                      ("installation", "Installation")],
                                     string="Job Card Type", help="Job Card Type : Manages flow of job card.")
    replacement_type = fields.Selection([("identical", "Identical Device"),
                                         ("higher_no_fees", "Higher Device (Without Additional Fees)"),
                                         ("higher_with_fees", "Higher Device (With Additional Fees)")],
                                        string="Replacement Type")

    #Smart Button Fields
    delivery_count = fields.Integer("Delivery", compute="get_delivery_count", store=False,
                                    help="Delivery count for this jobcard ticket.")
    invoice_count = fields.Integer("Invoice", compute="get_invoice_count", store=False,
                                    help="Invoice count for this jobcard ticket.")
    order_count = fields.Integer("Order", compute="get_order_count", store=False,
                                 help="Sale Order Count for this jobcard ticket.")

    def name_get(self):
        result = []
        for ticket in self:
            if ticket.name and ticket.id:
                result.append((ticket.id, "%s (#%d)" % (ticket.name, ticket.id)))
        return result

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New' and self.env.user.branch_id.name:
            vals['sequence'] = self.env.user.branch_id.name +'-'+str(datetime.datetime.now().strftime("%y"))+'-'+self.env['ir.sequence'].next_by_code('helpdesk.ticket') or 'New'
        result = super(HelpdeskTicket, self).create(vals)
        return result

    @api.onchange("customer_complaints_id")
    def onchange_customer_complaints(self):
        records = []
        for rec in self.customer_complaints_id:
            if rec.is_other:
                records.append(rec)
        if records:
            self.is_other = True
        else:
            self.is_other = False

    def get_order_count(self):
        sale_order_obj = self.env["sale.order"]
        for ticket in self:
            ticket.order_count = len(sale_order_obj.search([("job_card_id", '=', ticket.id)]).ids)

    def write(self, vals):
        helpdesk_stage_obj = self.env["helpdesk.stage"]

        job_cards = self.filtered(lambda ticket: ticket.is_job_card)
        helpdesk_tickets = self.filtered(lambda ticket: not ticket.is_job_card)

        for job_card in job_cards:
            warranty = job_card.sale_order_id.warranty_details.filtered(lambda sw: sw.product_id == job_card.sale_order_line_id.product_id)
            vals_stage_id = vals.get("stage_id", False) and helpdesk_stage_obj.browse(vals.get("stage_id")) or False

            if vals.get("warranty_end_date", False):
                if self.env.user.has_group("maintenance_management.group_maintenance_supervisor") or self.env.user.has_group("maintenance_management.group_maintenance_manager"):
                    if job_card.stage_id.is_close:
                        raise Warning(_("Warranty End Date can not be changed for closed job cards."))

                elif self.env.user.has_group("maintenance_management.group_maintenance_technician"):
                    if not job_card.stage_id.is_new or vals_stage_id and not vals_stage_id.is_new:
                        raise Warning(_("Technicians are allowed to change warranty end date only in 'New' Stage."))

                else:
                        raise Warning(_("Only 'Maintenance Users' are allowed to change Warranty End Date in Job Card."))

            if job_card.stage_id.is_new and not vals_stage_id:
                super(HelpdeskTicket, job_card).write(vals)
            elif vals_stage_id and not vals_stage_id.is_cancel and not job_card.job_card_type and not vals.get('job_card_type', False):
                raise Warning(_("Please set Job Card Type in job card '%s' to proceed." % job_card.display_name))
            else:
                super(HelpdeskTicket, job_card).write(vals)

            if vals.get("warranty_end_date", False) and vals.get("warranty_end_date") == str(job_card.warranty_end_date):
                warranty.end_date = job_card.warranty_end_date

        super(HelpdeskTicket, helpdesk_tickets).write(vals)

        return True

    def unlink(self):
        if self.mapped("is_job_card") and False in self.mapped("stage_id").mapped("allow_delete"):
            raise Warning("Job Card can not be deleted, Allow deletion from stages.")
        super(HelpdeskTicket, self).unlink()

    def get_delivery_count(self):
        stock_picking_obj = self.env["stock.picking"]
        sale_order_obj = self.env["sale.order"]
        for ticket in self:
            delivery_count = len(stock_picking_obj.search([('jobcard_ticket_id', "=", ticket.id)]).ids)
            sale_orders = sale_order_obj.search([("job_card_id", '=', ticket.id)])
            if sale_orders and sale_orders.mapped("picking_ids"):
                delivery_count += len(sale_orders.mapped("picking_ids").ids)
            ticket.delivery_count = delivery_count


    def get_invoice_count(self):
        account_move_obj = self.env["account.move"]
        sale_order_obj = self.env["sale.order"]
        for ticket in self:
            invoice_count = len(account_move_obj.search([('jobcard_ticket_id', "=", ticket.id)]).ids)
            sale_orders = sale_order_obj.search([("job_card_id", '=', ticket.id)])
            if sale_orders and sale_orders.mapped("invoice_ids"):
                invoice_count += len(sale_orders.mapped("invoice_ids").ids)
            ticket.invoice_count = invoice_count

    @api.constrains("warranty_type", "job_card_type")
    def job_card_type_constrains(self):
        for ticket in self:
            if ticket.warranty_type == 'out_of_warranty' and ticket.job_card_type != 'repair':
                raise Warning(_("When maintenance is out of warranty, only 'Repair' job cards can be created."))

    @api.onchange("sale_order_line_id")
    def sale_order_line_onchange(self):
        for ticket in self:
            warranty = ticket.sale_order_id.warranty_details.filtered(lambda sw: sw.product_id == ticket.sale_order_line_id.product_id)
            stock_move_line = ticket.sale_order_id.picking_ids.mapped('move_line_ids_without_package').filtered(lambda sml: sml.product_id == ticket.sale_order_line_id.product_id)
            ticket.product_id = ticket.sale_order_line_id.product_id.id
            ticket.item_code = ticket.sale_order_line_id.product_id.default_code
            ticket.item_description = ticket.sale_order_line_id.product_id.display_name
            ticket.lot_id = stock_move_line.lot_id.id
            ticket.warranty_end_date = warranty.end_date

    @api.onchange("sale_order_id")
    def sale_order_onchange(self):
        for ticket in self:
            ticket.warehouse_id = ticket.sale_order_id.warehouse_id.id
            ticket.partner_id = ticket.sale_order_id.partner_id.id

    @api.onchange("product_id")
    def product_id_onchange(self):
        self.ensure_one()
        if self.product_id:
            self.item_code = self.product_id.default_code
            self.item_description = self.product_id.display_name
            self.device_category_id = self.product_id.categ_id.id

    def check_if_spare_part_remaining(self):
        self.ensure_one()
        stock_picking_obj = self.env["stock.picking"]
        pickings = stock_picking_obj.search([('jobcard_ticket_id', "=", self.id), ('state', '!=', 'cancel')])
        transfer_remaining = False
        for line in self.workorder_lines:
            move = pickings.mapped("move_ids_without_package").filtered(lambda mv : mv.product_id == line.product_id)
            if not move:
                transfer_remaining = True
                break
            if move and sum(move.mapped("product_uom_qty")) < line.quantity:
                transfer_remaining = True
                break
        return transfer_remaining

    def request_spare_parts(self):
        """
        This process will create delivery pickings to request spare parts from warehouse.
        """
        stock_picking_obj = self.env["stock.picking"]
        stock_move_obj = self.env["stock.move"]
        stock_move_line_obj = self.env["stock.move.line"]
        for ticket in self:
            create_transfer = ticket.check_if_spare_part_remaining()
            if not create_transfer:
                raise Warning(_("All Spare Parts Already Transferred."))

            if not ticket.workorder_lines:
                raise Warning(_("No Workorder Lines To Request Spare Parts."))

            existing_pickings = stock_picking_obj.search([('jobcard_ticket_id', "=", self.id), ('state', '!=', 'cancel')])
            picking_fields = stock_picking_obj.fields_get()
            picking_data = stock_picking_obj.default_get(picking_fields)
            out_picking_type = ticket.warehouse_id.out_type_id
            picking_data.update({
                "picking_type_id": out_picking_type.id,
            })
            temp_picking = stock_picking_obj.new(picking_data)
            temp_picking.onchange_picking_type()
            out_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
            move_vals = []
            move_line_vals = []
            for line in ticket.workorder_lines:
                quantity = line.quantity
                existing_move_lines_qty = sum(existing_pickings.mapped("move_line_ids_without_package").filtered(lambda move: move.product_id == line.product_id).mapped("qty_done"))
                if existing_move_lines_qty >= line.quantity:
                    continue
                elif existing_move_lines_qty < line.quantity and existing_move_lines_qty > 0:
                    quantity -= existing_move_lines_qty

                #Stock Move
                tmp_stock_move = stock_move_obj.new({
                    "product_id": line.product_id.id,
                    "name": line.product_id.display_name,
                    "product_uom": line.uom_id.id,
                    "product_uom_qty": quantity
                })
                tmp_stock_move.onchange_product()
                tmp_stock_move.onchange_quantity()
                stock_move_vals = tmp_stock_move._convert_to_write(tmp_stock_move._cache)
                if 'product_qty' in list(stock_move_vals.keys()):
                    stock_move_vals.pop('product_qty')
                    move_vals.append((0, 0, stock_move_vals))

                # Stock Move Line
                tmp_stock_move_line = stock_move_line_obj.new({
                    "product_id": line.product_id.id,
                    "product_uom_id": line.uom_id.id,
                    "qty_done": line.quantity,
                    "location_id": out_picking_vals.get("location_id", False),
                    "location_dest_id": out_picking_vals.get("location_dest_id", False)
                })
                tmp_stock_move_line.onchange_product_id()
                tmp_stock_move_line._onchange_qty_done()
                stock_move_line_vals = tmp_stock_move_line._convert_to_write(tmp_stock_move_line._cache)
                move_line_vals.append((0, 0, stock_move_line_vals))

            out_picking_vals.update({
                'partner_id': ticket.partner_id.id,
                'move_ids_without_package': move_vals,
                'move_line_ids_without_package': move_line_vals,
                'jobcard_ticket_id': ticket.id,
            })
            out_picking = stock_picking_obj.create(out_picking_vals)
            ticket.workorder_lines.picking_id = out_picking.id

    def action_view_orders(self):
        action = self.env.ref('sale.action_orders').read()[0]
        sale_order_obj = self.env["sale.order"]
        orders = sale_order_obj.search([('job_card_id', "=", self.id)])
        if len(orders) > 1:
            action['domain'] = [('id', 'in', orders.ids)]
        elif orders:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = orders.id
        action['context'] = dict(self._context, default_partner_id=self.partner_id.id)
        return action

    def action_view_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        stock_picking_obj = self.env["stock.picking"]
        sale_order_obj = self.env["sale.order"]
        orders = sale_order_obj.search([('job_card_id', "=", self.id)])
        pickings = stock_picking_obj.search([('jobcard_ticket_id', "=", self.id)])
        pickings += orders.mapped("picking_ids")
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
        invoice_obj = self.env["account.move"]
        sale_order_obj = self.env["sale.order"]
        orders = sale_order_obj.search([('job_card_id', "=", self.id)])
        invoices = invoice_obj.search([('jobcard_ticket_id', '=', self.id)])
        invoices += orders.mapped("invoice_ids")
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

    def return_and_refund_device(self):
        self.create_return_picking()
        self.create_refund_invoice()
        return True

    def create_return_picking(self):
        stock_picking_obj = self.env["stock.picking"]
        stock_return_picking_obj = self.env["stock.return.picking"]
        sale_order_id = False
        for ticket in self:
            if not ticket.sale_order_id:
                stock_picking_id = self.env["stock.picking"].search([('move_line_ids_without_package.lot_id', '=', ticket.lot_id.id)])
                sale_order_id = self.env["sale.order"].search([('picking_ids.id', 'in', stock_picking_id.ids)], order='id desc', limit=1)
            else:
                sale_order_id = ticket.sale_order_id
            try:
                if ticket.replacement_return_picking_id:
                    continue
                if sale_order_id and not sale_order_id.picking_ids.filtered(lambda picking: picking.state == 'done'):
                    raise Warning(_("No transferred deliveries in sale order %s to return." % sale_order_id.name))

                if not ticket.warehouse_id.wh_scrap_location_id.id:
                    raise Warning(_("Configure scrap location in warehouse %s" % ticket.warehouse_id.display_name))

                pickings = sale_order_id.picking_ids.filtered(lambda picking: picking.state == 'done' and picking.mapped("move_lines").mapped("product_id") in ticket.product_id)
                pickings_to_return = pickings and pickings[0] or False
                if not pickings_to_return:
                    raise Warning(_("No Transferred Picking in order : %s. Can not generate return picking." % sale_order_id.name))

                return_picking_data = {"picking_id": pickings_to_return.id}
                temp_picking = stock_return_picking_obj.new(return_picking_data)
                temp_picking._onchange_picking_id()
                return_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
                return_lines = []
                for product_return_move in return_picking_vals.get('product_return_moves', []):
                    vals = len(product_return_move) == 3 and product_return_move[2]

                    if not vals or not isinstance(vals, dict):
                        return_lines.append(product_return_move)
                        continue

                    if vals.get('product_id', False) == ticket.product_id.id:
                        return_lines.append(product_return_move)

                return_picking_vals.update({"product_return_moves": return_lines})
                return_picking_wiz = stock_return_picking_obj.create(return_picking_vals)
                new_picking_id, picking_type_id = return_picking_wiz._create_returns()
                new_picking = stock_picking_obj.browse(new_picking_id)
                new_picking.location_dest_id = ticket.warehouse_id.wh_scrap_location_id.id
                new_picking.jobcard_ticket_id = ticket.id
                ticket.replacement_return_picking_id = new_picking.id
            except Exception as e:
                raise Warning(_("Something went wrong while return delivery : %s" % e))
                continue
        return True

    def create_refund_invoice(self):
        account_move_reversal_obj = self.env["account.move.reversal"]
        account_move_obj = self.env["account.move"]
        sale_order_id = False
        for ticket in self:
            if not ticket.sale_order_id:
                stock_picking_id = self.env["stock.picking"].search([('move_line_ids_without_package.lot_id', '=', ticket.lot_id.id)])
                sale_order_id = self.env["sale.order"].search([('picking_ids.id', 'in', stock_picking_id.ids)], order='id desc', limit=1)
            else:
                sale_order_id = ticket.sale_order_id
            if ticket.replacement_refund_invoice_id:
                continue
            if sale_order_id and not sale_order_id.invoice_ids.filtered(lambda invoice: invoice.state == 'posted' and invoice.amount_residual < invoice.amount_total):
                raise Warning(_("No paid invoices in sale order %s to refund." % sale_order_id.name))

            invoices = sale_order_id.invoice_ids.filtered(lambda invoice: invoice.state == 'posted' and invoice.amount_residual < invoice.amount_total)
            invoice_to_refund = invoices and invoices[0] or False
            if not invoice_to_refund:
                raise Warning(_("No paid invoices in sale order %s to refund." % sale_order_id.name))

            ctx = {'active_id': invoice_to_refund.id, 'active_ids': invoice_to_refund.ids, 'active_model': 'account.move'}
            refund_invoice_fields = account_move_reversal_obj.fields_get()
            refund_invoice_wiz_data = account_move_reversal_obj.with_context(ctx).default_get(refund_invoice_fields)
            refund_invoice_wiz = account_move_reversal_obj.create(refund_invoice_wiz_data)
            refund_action = refund_invoice_wiz.with_context(ctx).reverse_moves()
            reverse_moves = refund_action.get("res_id", False) and account_move_obj.browse(refund_action.get('res_id')) or refund_action.get('domain', False) and account_move_obj.search(refund_action.get('domain')) or False
            reverse_moves.line_ids.filtered(lambda line: line.product_id and line.product_id != ticket.product_id).unlink()
            reverse_moves and reverse_moves.write({'jobcard_ticket_id': ticket.id})
            ticket.replacement_refund_invoice_id = reverse_moves and reverse_moves.ids[0] or False
        return True

    def replace_and_generate_invoice(self):
        self.create_replacement_delivery()
        self.crate_replacement_invoice()
        return True

    def create_replacement_delivery(self):
        stock_picking_obj = self.env["stock.picking"]
        stock_move_obj = self.env["stock.move"]
        stock_move_line_obj = self.env["stock.move.line"]
        for ticket in self:
            if ticket.replacement_picking_id:
                continue
            if not ticket.replacement_product_id:
                raise Warning(_("No Replacement Product to create a replacement delivery."))
            picking_fields = stock_picking_obj.fields_get()
            picking_data = stock_picking_obj.default_get(picking_fields)
            out_picking_type = ticket.warehouse_id.out_type_id
            picking_data.update({
                "picking_type_id": out_picking_type.id,
            })
            temp_picking = stock_picking_obj.new(picking_data)
            temp_picking.onchange_picking_type()
            out_picking_vals = temp_picking._convert_to_write(temp_picking._cache)

            tmp_stock_move = stock_move_obj.new({
                "product_id": ticket.replacement_product_id.id,
                "name": ticket.replacement_product_id.display_name,
                "product_uom": ticket.replacement_product_id.uom_id.id,
                "product_uom_qty": 1.0,
            })
            tmp_stock_move.onchange_product()
            tmp_stock_move.onchange_quantity()
            stock_move_vals = tmp_stock_move._convert_to_write(tmp_stock_move._cache)
            if 'product_qty' in list(stock_move_vals.keys()):
                stock_move_vals.pop('product_qty')
            move_vals = [((0, 0, stock_move_vals))]

            # Stock Move Line
            tmp_stock_move_line = stock_move_line_obj.new({
                "product_id": ticket.replacement_product_id.id,
                "product_uom_id": ticket.replacement_product_id.uom_id.id,
                "qty_done": 1.0,
                "location_id": out_picking_vals.get("location_id", False),
                "location_dest_id": out_picking_vals.get("location_dest_id", False)
            })
            tmp_stock_move_line.onchange_product_id()
            tmp_stock_move_line._onchange_qty_done()
            stock_move_line_vals = tmp_stock_move_line._convert_to_write(tmp_stock_move_line._cache)
            move_line_vals = [(0, 0, stock_move_line_vals)]

            out_picking_vals.update({
                'partner_id': ticket.partner_id.id,
                'move_ids_without_package': move_vals,
                'move_line_ids_without_package': move_line_vals,
                'jobcard_ticket_id': ticket.id,
            })
            new_picking = stock_picking_obj.create(out_picking_vals)
            ticket.replacement_picking_id = new_picking.id
        return True

    def crate_replacement_invoice(self):
        invoice_obj = self.env["account.move"]
        sale_order_id = False
        for ticket in self:
            if not ticket.sale_order_id:
                stock_picking_id = self.env["stock.picking"].search([('move_line_ids_without_package.lot_id', '=', ticket.lot_id.id)])
                sale_order_id = self.env["sale.order"].search([('picking_ids.id', 'in', stock_picking_id.ids)], order='id desc', limit=1)
            else:
                sale_order_id = ticket.sale_order_id

            if ticket.replacement_invoice_id:
                continue

            invoice_vals = sale_order_id._prepare_invoice()
            invoice_line_vals = []

            #Invoice line
            sale_lines = sale_order_id.order_line.filtered(lambda line: line.product_id == ticket.product_id)
            sale_order_line = sale_lines and sale_lines[0] or False
            if not sale_order_line:
                raise Warning(_("No Line with product %s in sale order %s" % (ticket.product_id.displat_name, sale_order_id.name)))
            invoice_line_data = sale_order_line._prepare_invoice_line()
            new_product_price_unit = self.replacement_product_id.uom_id._compute_price(self.replacement_product_id.lst_price, self.replacement_product_id.uom_id)
            invoice_line_data.update({
                'product_id': ticket.replacement_product_id.id,
                'name': ticket.replacement_product_id.display_name,
                'quantity': invoice_line_data.get('quantity', 1) if invoice_line_data.get('quantity', 1) > 0 else 1,
                'price_unit': new_product_price_unit
            })
            invoice_line_vals.append((0, 0, invoice_line_data))

            old_product_price_unit = self.product_id.uom_id._compute_price(self.product_id.lst_price, self.product_id.uom_id)
            new_product_price_unit = self.replacement_product_id.uom_id._compute_price(self.replacement_product_id.lst_price, self.replacement_product_id.uom_id)

            #Invonce Discount Line (For replacement with higher devices.
            if ticket.job_card_type == "replace" and ticket.replacement_type in ["higher_no_fees", "higher_with_fees"]:
                price_unit = 0.0
                if new_product_price_unit > old_product_price_unit:
                    price_unit = new_product_price_unit - old_product_price_unit
                sale_disc_lines = sale_order_id.order_line.filtered(lambda line: line.product_id == ticket.product_id)
                sale_order_line = sale_disc_lines and sale_disc_lines[0] or False
                if not sale_disc_lines:
                    raise Warning(_("No Line with product %s in sale order %s" % (ticket.product_id.displat_name, sale_order_id.name)))
                invoice_line_data = sale_order_line._prepare_invoice_line()
                invoice_line_data.update({
                    'product_id': ticket.discount_product_id.id,
                    'price_unit': price_unit * -1,
                    'quantity': invoice_line_data.get('quantity', 1) if invoice_line_data.get('quantity', 1) > 0 else 1
                })
                if price_unit > 0:
                    invoice_line_vals.append((0, 0, invoice_line_data))

            #Add invoice line vals in invoice vals and create invoice.
            invoice_vals.update({
                'invoice_line_ids': invoice_line_vals,
                'jobcard_ticket_id': ticket.id,
            })

            if ticket.is_distributor_jobcard and ticket.invoice_partner == 'distributor':
                invoice_vals.update({'partner_id': ticket.distributor_id.id})
            else:
                invoice_vals.update({'partner_id': ticket.partner_id.id})

            new_invoice = invoice_obj.create(invoice_vals)

            if ticket.job_card_type == "replace" and ticket.replacement_type == "higher_with_fees":
                invoice_vals = sale_order_id._prepare_invoice()
                if new_product_price_unit > old_product_price_unit:
                    price_unit = new_product_price_unit - old_product_price_unit

                # Invoice line
                new_sale_lines = sale_order_id.order_line.filtered(lambda line: line.product_id == ticket.product_id)
                sale_order_line = new_sale_lines and new_sale_lines[0] or False
                if not sale_order_line:
                    raise Warning(_("No Line with product %s in sale order %s" % (ticket.product_id.displat_name, sale_order_id.name)))
                invoice_line_data = sale_order_line._prepare_invoice_line()
                invoice_line_data.update({
                    'product_id': ticket.replacement_product_id.id,
                    'name': ticket.replacement_product_id.display_name,
                    'price_unit': price_unit,
                    'quantity': invoice_line_data.get('quantity', 1) if invoice_line_data.get('quantity', 1) > 0 else 1
                })
                invoice_line_vals = [(0, 0, invoice_line_data)]

                invoice_vals.update({
                    'invoice_line_ids': invoice_line_vals,
                    'jobcard_ticket_id': ticket.id,
                })

                new_invoice = invoice_obj.create(invoice_vals)

            ticket.replacement_invoice_id = new_invoice.id

        return True

    def return_device_to_scrap(self):
        stock_picking_obj = self.env["stock.picking"]
        stock_return_picking_obj = self.env["stock.return.picking"]
        for ticket in self:
            try:
                if ticket.return_to_scrap_picking_id:
                    continue

                if not ticket.warehouse_id:
                    raise Warning(_("No Warehouse in ticket %s to return." % ticket.name))

                if not ticket.warehouse_id.wh_scrap_location_id:
                    raise Warning(_("Scrap location not set in warehouse %s to return." % ticket.warehouse_id.name))

                if not ticket.sale_order_id.picking_ids.filtered(lambda picking: picking.state == 'done'):
                    raise Warning(
                        _("No transferred deliveries in sale order %s to return." % ticket.sale_order_id.name))

                scrap_pickings = ticket.sale_order_id.picking_ids.filtered(lambda picking: picking.state == 'done' and picking.mapped("product_id") in ticket.product_id)
                pickings_to_return = scrap_pickings and scrap_pickings[0] or False
                if not pickings_to_return:
                    raise Warning(_("No transferred deliveries in sale order %s to return." % ticket.sale_order_id.name))
                return_picking_data = {"picking_id": pickings_to_return.id}
                temp_picking = stock_return_picking_obj.new(return_picking_data)
                temp_picking._onchange_picking_id()
                return_picking_vals = temp_picking._convert_to_write(temp_picking._cache)
                return_lines = []
                for product_return_move in return_picking_vals.get('product_return_moves', []):
                    vals = len(product_return_move) == 3 and product_return_move[2]

                    if not vals or not isinstance(vals, dict):
                        return_lines.append(product_return_move)
                        continue

                    if vals.get('product_id', False) == ticket.product_id.id:
                        return_lines.append(product_return_move)

                return_picking_vals.update({
                    "product_return_moves": return_lines
                })
                return_picking_wiz = stock_return_picking_obj.create(return_picking_vals)
                new_picking_id, picking_type_id = return_picking_wiz._create_returns()
                new_picking = stock_picking_obj.browse(new_picking_id)
                new_picking.location_dest_id = ticket.warehouse_id.wh_scrap_location_id.id
                new_picking.jobcard_ticket_id = ticket.id
                ticket.return_to_scrap_picking_id = new_picking.id
            except Exception as e:
                warning_message = "Something went wrong while return delivery : %s" % e
                _logger.warning(warning_message)
                raise Warning(_(warning_message))
                continue
        return True


class HelpdeskWorkorder(models.Model):
    _name = "helpdesk.workorder"
    _description = "Helpdesk Workorder"
    _order = "id"

    product_id = fields.Many2one("product.product", string="Product", required=True)
    helpdesk_ticket_id = fields.Many2one("helpdesk.ticket", string="Job Card")
    name = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit Of Measure")
    quantity = fields.Float("Quantity")
    price_unit = fields.Float("Price Unit")
    tax_ids = fields.Many2many("account.tax", "helpdesk_workorder_tax_rel", "helpdesk_workorder_id", "account_tax_id",
                               string="Taxes", help="Apply taxes for products.")
    tax_amount = fields.Float("VAT", compute="get_tax_amount", store=False)
    sub_total = fields.Float("Sub Total", compute="get_subtotal_amount", store=False)

    @api.constrains("quantity")
    def quantity_constrains(self):
        for record in self:
            if record.quantity and record.quantity < 0:
                raise Warning(_("Quantity Can Not Be Less Than 0."))

    @api.depends("tax_ids", "price_unit", "quantity")
    def get_subtotal_amount(self):
        for record in self:
            record.sub_total = (record.quantity * record.price_unit) + record.tax_amount

    @api.depends("tax_ids", "price_unit", "quantity")
    def get_tax_amount(self):
        for record in self:
            total_tax_amount = 0.0
            for tax in record.tax_ids:
                tax_data = tax.compute_all(record.price_unit, currency=record.helpdesk_ticket_id.partner_id.currency_id,
                                           quantity=record.quantity, product=record.product_id,
                                           partner=record.helpdesk_ticket_id.partner_id)
                total_tax_amount += tax_data.get("total_included", 0) - tax_data.get("total_excluded", 0)
            record.tax_amount = total_tax_amount

    @api.onchange("product_id")
    def product_id_onchange(self):
        self.ensure_one()
        if self.product_id:
            self.name = self.product_id.display_name
            self.uom_id = self.product_id.uom_id
            self.price_unit = self.product_id.uom_id._compute_price(self.product_id.lst_price, self.product_id.uom_id)
            if not self.quantity or self.quantity < 0:
                self.quantity = 1


class CustomerComplaints(models.Model):
    _name = "customer.complaints"
    _description = "Customer Complaints"


    name = fields.Char("Name", required=True)
    arabic_name = fields.Char("Arabic")
    is_other = fields.Boolean("Other?", default=False)


    def name_get(self):
        result = []
        for rec in self:
            if rec.name and rec.arabic_name:
                name = rec.name + ' ' + rec.arabic_name
                result.append((rec.id, name))
        return result
