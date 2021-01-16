# -*- coding: utf-8 -*-
{
    'name': "Partner Open Balance ",

    'summary': """
             Open Balance Customization
        """,

    'description': """
        1. partner Open Balance 
       
        
    """,

    'author': "jk",
    'website': "https://jk.in/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
          'security/ir.model.access.csv',
          'views/open_balance_view.xml',
          'views/account_move_view.xml',
          'views/open_bal_payment.xml',
    ],


    'installable': True,
    'auto_install': False,
}