# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Reports Stamp & Sign',
    'version': '1.0',
    'summary': "This module contains sign & stamp in Job card PDF report.",
    'description': """
    """,
    'category': 'Sales/Accounting',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['maintenance_management'],
    'data': [
        'view/res_company_view.xml',
        'view/res_user_view.xml',
        # 'view/job_card_report.xml',
        ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}