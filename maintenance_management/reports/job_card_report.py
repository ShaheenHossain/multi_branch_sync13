# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ReportJobCard(models.AbstractModel):
    _name = 'report.maintenance_management.report_job_cards'
    _description = 'Job Cards Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'helpdesk.ticket',
            'docs': self.env['helpdesk.ticket'].browse(docids),
            'report_type': data.get('report_type') if data else '',
        }