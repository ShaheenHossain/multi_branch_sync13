# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Users(models.Model):
    _inherit = "res.users"

    user_signature = fields.Binary(string="User Signature")
