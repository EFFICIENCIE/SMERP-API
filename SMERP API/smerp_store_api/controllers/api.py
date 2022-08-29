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
        '/smerp/api/signup/user',
    ], auth="public", website=True, methods=['POST'], csrf=False, type='json')
    def api_signup_user(self, **post):
        if not post.get('password'):
            return {'error': _('password missing')}
        if not post.get('phone'): 
            return {'error': _('phone number missing')}
        if not post.get('email'): 
            return {'error': _('email missing')}
        values = {
            'login': post.get('email'),
            'phone': post.get('phone'),
            'password': post.get('password'),
            'name': post.get('email'),
        }
        try:
            db, login, password = request.env['res.users'].sudo().signup(values, False)
            request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
            uid = request.session.authenticate(db, login, password)
            if not uid:
                return {'error': 'Error during signup process'}
            current_user = request.env['res.users'].sudo().browse([uid])
            return {
                'message': 'signup successfull',
                'uid': uid,
                'token': current_user.get_user_access_token(),
            }
        except Exception as e:
            return {'error': 'Error during signup process :: {}'.format(str(e))}

    @http.route([
        '/smerp/api/change/password',
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
            return {'message': 'successfully changed password'}
        except Exception as e:
            return {'error': 'Can not change password :: {}'.format(str(e))}