# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Maintenance Management',
    'version': '1.0',
    'summary': "This module contains process regarding Maintenance Management.",
    'description': """
    """,
    'category': 'Sales/Accounting',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['helpdesk', 'road_master'],
    'data': [
        "data/maintenance_data.xml",
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "wizard/request_stock_wizard_view.xml",
        "views/helpdesk_stage_view.xml",
        "views/helpdesk_ticket_view.xml",
        "views/stock_warehouse_view.xml",
        "views/product_template_view.xml",
        "views/sale_order_view.xml",
        "views/helpdesk_team_view.xml",
        "views/job_card_report.xml",
        "views/stock_picking_view.xml"
        ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}