# -*- coding: utf-8 -*-

from odoo import models,fields


class SimCard(models.Model):
    _name = "sim.card"
    _description = "Sim Card"
    _order = "id desc"
    _rec_name = 'serial_no'

    # name = fields.Char("Name", copy=False, required=1)
    serial_no = fields.Char("Serial No.", copy=False, required=1)
    activation_date = fields.Date("Activation Date")
    mobile_no = fields.Char("Mobile No.", copy=False)
    associated_plate_no = fields.Char("Associated Plate No.", copy=False)
    associated_contract_id = fields.Many2one("sale.subscription", copy=False, string="Contract")
    state = fields.Selection([("inactive", "Inactive"),
                              ("active", "Active")],
                             string="Status", copy=False, default="inactive", required=True)
    partner_id = fields.Many2one("res.partner", copy=False, string="Provider")
    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)
