# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_url = fields.Char(string='API URL', config_parameter='whatsapp_base.api_url')
    api_token = fields.Char(string='API Token', config_parameter='whatsapp_base.api_token')
    api_instance_id = fields.Char(string='API Instance Id', config_parameter='whatsapp_base.api_instance_id')
