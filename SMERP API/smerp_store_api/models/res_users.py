# -*- coding: utf-8 -*-
import uuid
from odoo import fields, models, api
from odoo.osv import expression
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

    token = fields.Char()
    '''Device ID and Token is set to use in FCM (Firebase Push Notification Later)
       Fields can be kept hide from the screen, incase not needed else where only the 
       value of these related data can be pulled and trigger to Notification when we need.
    '''
    device_id = fields.Char(string="Device ID")
    device_token = fields.Char(string="Device Token")
    device_type = fields.Selection([
        ('android', 'Android'),
        ('ios', 'iOS')], string='Device Type')

    def get_user_access_token(self):
        return uuid.uuid4().hex

    def _check_credentials(self, password):
        try:
            super(ResUsers, self)._check_credentials(password)
        except AccessDenied:
            if self.env.user.token == password:
                pass
            else:
                raise AccessDenied()

    # @api.model
    # def _get_login_domain(self, login):
    #     """Override to add our custom domain so that user can login with either email address or through the phone"""
    #     super_domain = super(ResUsers, self)._get_login_domain(login)
    #     domain = expression.OR([
    #         super_domain,
    #         [('phone', '=', login)]
    #     ])
    #     return domain
