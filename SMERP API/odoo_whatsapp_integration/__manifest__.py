{
    'name': "Whatsapp Odoo Integration",
    'summary': """
        This module allows you to send whatsapp messages about the sale orders, purchase orders, 
        invoice order amount, and delivery orders along with order items to the respective user.""",

    'description': """
    """,
    'author': "Odoo SA",
    'website': "http://www.odoo.com",
    'category': 'Whatsapp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'web', 'stock', 'purchase','account','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/sms_security.xml',
        'wizard/wizard_multiple_contact.xml',
        'views/views.xml',
        'views/template.xml',
        'views/setting_inherit_view.xml',
        'wizard/message_wizard.xml',
        'wizard/wizard.xml',
        'wizard/wizard_contact.xml',
        'wizard/share_action.xml',
    ],
    'images':['static/description/main.gif'],
}
