# -*- coding: utf-8 -*-
{
    'name': "WhatsApp Base",

    'summary': """
       Whatsapp Base connector for waMarketing""",

    'description': """
        Whatsapp Base connector for waMarketing, used some of SMS features to use for credentials settings. 
    """,

    'author': "Abhishek Kumar",
    'website': "www.smerp.io",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'tools',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sms', 'base_setup'],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
}
