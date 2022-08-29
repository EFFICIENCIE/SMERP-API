# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = 'sms.sms'

    IAP_TO_SMS_STATE = {
        'success': 'sent',
        'error': 'sms_server',
    }