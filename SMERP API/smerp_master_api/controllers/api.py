# -*- coding: utf-8 -*-
import json
import datetime
from turtle import pos
import werkzeug
from werkzeug.urls import url_join
import base64

import odoo
from odoo import http, _, SUPERUSER_ID
from odoo import fields as odoo_fields
from odoo.http import request
from odoo.addons.web.controllers import main
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from odoo.exceptions import UserError, AccessError


class SMERPRestAPI(http.Controller):

    @http.route([
        '/smerp/platform/plan',
    ], auth="public", website=True, methods=['POST'], csrf=False, type='json')
    def api_reset_password(self, **post):
        if not post.get('login'):
            return {'error': 'username missing'}
        if not post.get('password'):
            return {'error': _('password missing')}
        if not post.get('new_password'): 
            return {'error': _('new password missing')}

        try:
            uid = request.session.authenticate(request.session.db, post['login'], post['password'])
            if not uid:
                return {'error': 'Authentication Failed!'}
            current_user = request.env['res.users'].sudo().browse([uid])
            current_user.update({'password': post['new_password'], 'token': False})
            return {'message': 'successfully reset password'}
        except Exception as e:
            return {'error': 'Can not reset password :: {}'.format(str(e))}