# -*- coding: utf-8 -*-
{
    'name': "GURU send Invoice",

    'summary': """
        Electronic Online invoicing by Bolivia's statements""",

    'description': """
        Online invoicing
    """,

    'author': "MF Consulting",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'fact_electronica'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_views.xml',
        'views/siat_server_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}