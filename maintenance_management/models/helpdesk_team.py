# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import expression


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    is_jobcard_team = fields.Boolean("Job Card Team", default=False, help="This helpdesk team is for job cards.")

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if self._context.get("jobcard_team_check", False):
            if self._context.get("is_job_card", False):
                args = expression.AND([
                    args or [],
                    [('is_jobcard_team', '=', True)]
                ])
            else:
                args = expression.AND([
                    args or [],
                    [('is_jobcard_team', '!=', True)]
                ])
        return super(HelpdeskTeam, self)._name_search(name, args=args, operator=operator, limit=limit,
                                                      name_get_uid=name_get_uid)
