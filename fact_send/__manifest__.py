# -*- coding: utf-8 -*-
{
    'name': "API send Invoice",

    'summary': """
        Electronic Online invoicing by Bolivia's statements""",

    'description': """
        Online invoicing
    """,

    'author': "Mauricio Carreño S.",
    'website': "http://www.yourcompany.com",
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
