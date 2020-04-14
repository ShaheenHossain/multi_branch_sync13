# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Roadmaster Customization',
    'version': '1.0',
    'summary': "This module contains custom changes for RMTS Requirements.",
    'description': """
        - Add fields related to tracking device in products model.
    """,
    'category': 'Sales/Accounting',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ["multi_branches", "sale_subscription", 'mail', 'portal'],
    'data': [
        "data/ir_sequence_data.xml",
        "data/email_data.xml",
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "report/device_installation_report_template.xml",
        "report/device_installation_report.xml",
        "wizard/installment_product_selection.xml",
        "views/product_template_view.xml",
        "views/sim_card_view.xml",
        "views/stock_location_view.xml",
        "views/device_installation_view.xml",
        "views/sale_order_view.xml",
        "views/hardware_type_view.xml",
        "views/sale_subscription_view.xml",
        "views/installation_template_view.xml"
        ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}