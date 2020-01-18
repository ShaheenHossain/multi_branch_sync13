# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'POS Multi Branches',
    'version': '1.0',
    'summary': 'Application provides functionality of manage multi branches for companies.',
    'sequence': 30,
    'description': """
        This application provide functionality of manage multi branches for Company.
        Multi Branches functionality covered in POS.
        Also maintain User and Manager level access rights.
    """,
    'category': 'Point of Sale',
    'license': 'OPL-1',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['point_of_sale', 'multi_branches'],
    'data': [
        'security/security.xml',
        'views/pos_config_view.xml',
        'views/pos_payment_view.xml',
        ],
    'demo': [],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'images': [],
    'price': 0.0,
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
}
