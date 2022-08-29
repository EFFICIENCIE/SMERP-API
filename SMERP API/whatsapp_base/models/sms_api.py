# -*- coding: utf-8 -*-
import logging
import requests

from odoo import models, fields, api, _
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

API_URL = 'https://wamarketing.shop/api/send.php'

class WhatsAppConnection():

    def __init__(self, api_url, api_token, api_instance_id):
        self.api_url = api_url or API_URL
        self.api_token = api_token
        self.api_instance_id = api_instance_id

    def _connect_with_whatsapp_api(self, params=None, timeout=15):
        headers = {
            'Authorization': 'XXXXX',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        payload = {
            'number': params.get('numbers'),
            'type': 'text',
            'message': params.get('message'),
            'instance_id': self.api_instance_id,
            'access_token': self.api_token
        }

        _logger.info('connecting to .. %s', self.api_url)
        _logger.info('number to .. %s', payload)
        result = {}
        try:
            response = requests.get(self.api_url, timeout=3, params=payload, headers=headers, verify=False)
            response.raise_for_status()
            result = response.json()
            _logger.info('Received responsed from api :: {}'.format(result))
        except requests.exceptions.HTTPError as e:
            result['error'] = e.response.content
        except requests.exceptions.ConnectionError as e:
            result['error'] = str(e)
        except requests.exceptions.Timeout as e:
            result['error'] = _('Api server is unreachable')
        result['state'] = result['status']
        return result


class SmsApi(models.AbstractModel):
    _inherit = 'sms.api'

    @api.model
    def _send_sms(self, numbers, message):
        params = {
            'numbers': numbers,
            'message': message,
        }
        config_params = self.env['ir.config_parameter'].sudo()
        api_url = config_params.get_param('whatsapp_base.api_url')
        api_token = config_params.get_param('whatsapp_base.api_token')
        api_instance_id = config_params.get_param('whatsapp_base.api_instance_id')
        connection = WhatsAppConnection(api_url, api_token, api_instance_id)
        return connection._connect_with_whatsapp_api(params)

    @api.model
    def _send_sms_batch(self, messages):
        result = []
        for message in messages:
            res = self._send_sms(message['number'], message['content'])
            result.append({
                'res_id': message['res_id'],
                'state': res['state'],
                'message': res['message'],
            })
        return result
