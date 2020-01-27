# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResBranch(models.Model):
    _inherit = "res.branch"

    @api.model
    def create(self, vals):
        new_branch = super(ResBranch, self).create(vals)
        new_branch._create_mwh_location()
        return new_branch

    def _create_mwh_location(self):
        parent_location = self.env.ref('stock.stock_location_locations', raise_if_not_found=False)
        for company in self:
            location = self.env['stock.location'].create({
                'name': _('%s: Mobile Location') % self.name,
                'usage': 'transit',
                'location_id': parent_location and parent_location.id or False,
                'company_id': self.company_id.id,
                'branch_id': self.id,
                'mobile_location': True,
            })
            company.write({'internal_transit_location_id': location.id})
            company.partner_id.with_context(force_branch=self.id).write({
                'property_stock_customer': location.id,
                'property_stock_supplier': location.id,
            })
