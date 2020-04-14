# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Familiar / Similar Products',
    'version': '1.0',
    'summary': "This module is extension of products to manage familiar products and similar products.",
    'description': """
    """,
    'category': 'Sales',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['maintenance_management'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/change_product_wizard_view.xml",
        "views/product_template_view.xml",
        "views/helpdesk_ticket_view.xml",
        "views/similar_product_view.xml",
        "views/sale_order_view.xml"
    ],
    'demo': [],
    'images': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}