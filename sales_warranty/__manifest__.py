# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Repair Service - Warranty Management',
    'version': '1.0',
    'category': 'Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'summary': 'Allows to track product warranty details on sales order',
    'website': 'www.synconics.com',
    'description': """
Repair Service - Warranty Management
====================================
* This application allows to track product warranty details on sales order.
""",
    'depends': ['sale_management', 'sale_stock', 'sale_crm', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/warranty_data.xml',
        'views/warranty_view.xml',
        'views/product_view.xml',
        'views/res_partner_view.xml',
        'views/warranty_detail_view.xml',
        'views/sale_view.xml',
        'report/warranty_report.xml',
        'report/sales_report_template.xml',
        'menu.xml'
    ],
    'demo': [
        'demo/user_demo.xml',
        'demo/partner_demo.xml',
        'demo/warranty_demo.xml',
        'demo/product_warranty_demo.xml',
        'demo/saleorder_warranty_demo.xml',
    ],
    'images': ['static/description/main_screen.jpg'],
    'price': 60.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
