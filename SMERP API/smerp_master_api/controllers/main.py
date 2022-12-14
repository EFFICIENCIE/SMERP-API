# -*- coding: utf-8 -*-
import json
import datetime
import odoo
from odoo import http, _
from odoo import fields as odoo_fields
from odoo.http import request
from odoo.addons.web.controllers import main
import base64
from werkzeug.urls import url_join


class SmerpRestAPI(http.Controller):

    @http.route([
        '/smerp/api/user/get_token',
    ], auth="public", website=True, methods=['POST'], csrf=False, type='json')
    def api_get_token(self, **post):
        res = {}
        if not request.params.get('login') or not request.params.get('password'):
            return {'error': "No login or password found in parameters"}
        try:
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if uid:
                user = request.env['res.users'].sudo().browse(uid)
                web_base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                token = user.get_user_access_token()
                user.token = token
                user.device_id = request.params['device_id']
                user.device_token = request.params['device_token']
                user.device_type = request.params['device_type']
                res.update(
                    token=token,
                    id=user.id,
                    name=user.partner_id.name,
                    email=user.partner_id.email,
                    login_id=user.login,
                    phone=user.partner_id.phone,
                    icon=url_join(web_base_url, '/smerp/api/image/{}/{}/{}'.format(user.partner_id.id, 'image_512', 'res.partner'))
                )
                request.session.logout()
            else:
                res['error'] = "Wrong login/password"
        except Exception as e:
            res['error'] = "Something Went Wrong!  %s" % e
        return res

    @http.route([
        '/smerp/api/user/delete_token',
    ], auth="public", website=True, methods=['POST'], csrf=False, type='json')
    def api_delete_token(self, **post):
        """
            Delete token : it is medetory to pass token after this call token will be deleted.
        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        else:
            try:
                current_user.token = False
            except Exception as e:
                return {'error': _(' %s' % e)}

        return {'success': _('Token \'%s\' Deleted Successfully' % post.get('token'))}

    @http.route([
        '/smerp/api/user/refresh_token',
    ], auth="public", website=True, methods=['POST'], csrf=False, type='json')
    def api_refresh_token(self, **post):
        """
            Refresh token : it is medetory to pass token after this call token will return new token.
            It return {"token": "6656a5ba22ca440ca53fd40caeea38eb"}
        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        else:
            try:
                current_user.token = False
                token = current_user.get_user_access_token()
                current_user.token = token
                res = {}
                res.update(
                    token=token,
                    name=current_user.partner_id.name,
                    email=current_user.partner_id.email,
                    login_id=current_user.login,
                    phone=current_user.partner_id.phone,
                )
                return res
            except Exception as e:
                return {'error': _(' %s' % e)}

    @http.route(['/smerp/api/<string:model>/search', '/smerp/api/<string:model>/search/<int:id>'], auth="public", methods=['POST'], csrf=False, type='json',)
    def api_search_data(self, model=None, id=None, **post):
        """
            list records , it is medetory to pass model name
            if id is pass with url then return a single record of a specific id Found
            else check domain in post data , if domain is found then return matched records
            else return all the data with id and name field.

            By default a search will return the ids and name of all records matching the
            condition, which may be a huge number.if offset and limit parameters
            are available to only retrieve a subset of all matched records.

            eg. for single record
            localhost:8069/api/res.partner/search/1?token=24e635ff9cc74429bed3d420243f5aa6
            eg. for search using domain, offset and limit
            localhost:8069/api/res.partner/search?token=24e635ff9cc74429bed3d420243f5aa6&domain=[('id', '>=', 7)]&offset=10&limit=5

            By default a search will return the ids and name of all records matching the condition,
            it may possible that also you want to read other fields name with than name and ids.
            Note: it will always returns id as default field name if field name
            is not given it will return (id and name) otherwise it will return (id and all given fields name).
        """
        result = dict()
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
            if model == 'res.partner':
                Model = Model.sudo()

        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                domain = [('id', '=', id)]
                fields = []
            else:
                domain = post.get('domain') and eval(post['domain']) or []
                fields = ['name']
                if post.get('fields'):
                    fields = eval(post.get('fields'))
            result = Model.search_read(domain, fields=fields, offset=int(
                post.get('offset', 0)), limit=post.get('limit') and int(post['limit'] or None))
        result = self.parse_image(result)
        #result = self.parse_datetime(result)
        return result #json.dumps(result)

    @http.route(['/smerp/api/<string:model>/create'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def api_create_data(self, model=None, **post):
        """
            create record , it is medetory to pass model name
            and values for record creation pass as create_vals of JOSN/Dictionary format.
            eg.
            QueryString:
                localhost:8069/api/product.product/create?token=24e635ff9cc74429bed3d420243f5aa6&create_vals={'name':'Apple'}
            Return:
                If record is successfully created then it will return record id eg. {'id':101}
        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if post.get('create_vals'):
                create_vals = eval(post.get('create_vals'))
                if isinstance(create_vals, list):
                    res = []
                    for vals in create_vals:
                        try:
                            record = Model.create(vals)
                        except Exception as e:
                            return {'error': _(' %s' % e)}
                        if record:
                            res.append({'id': record.id})
                    return res #json.dumps(res)
                else:
                    try:
                        record = Model.create(create_vals)
                    except Exception as e:
                        return {'error': _(' %s' % e)}
                    if record:
                        res = {'id': record.id}
                        return res #json.dumps(res)
            else:
                return {'error': _('create_vals not found in query string')}

    @http.route(['/smerp/api/<string:model>/update', '/smerp/api/<string:model>/update/<int:id>'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def api_update_data(self, model=None, id=None, **post):
        """
            update record , it is medetory to pass model name and record id
            and values for record update pass as update_vals in JOSN/Dictionary format.
            eg.
            QueryString:
                localhost:8069/api/product.product/update/101?token=24e635ff9cc74429bed3d420243f5aa6&update_vals={'name':'Mango'}
            Return:
                If record is successfully updated then it will return {'success':'Record Updated Successfully'}
        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                if post.get('update_vals'):
                    try:
                        record = Model.browse(id)
                        update_vals = eval(post.get('update_vals'))
                        result = record.write(update_vals)
                        if result:
                            return {'success': _('Record Updated Successfully')}
                    except Exception as e:
                        return {'error': _('Model Not Found %s' % e)}
                else:
                    return {'error': _('update_vals not found in query string')}
            else:
                return {'error': _('id not found in query string')}

    @http.route(['/smerp/api/<string:model>/unlink/', '/smerp/api/<string:model>/unlink/<int:id>'
                 ], type='json', auth="public", csrf=False)
    def api_unlink_data(self, model=None, id=None, methods=['POST'], **post):
        """
            Delete record , it is medetory to pass model name and record id
            For Delete multiple records pass record ids in url parameter as 'unlink_ids' as in list format.
            eg.
            QueryString for Delete single record:
                localhost:8069/api/product.product/unlink/59?token=24e635ff9cc74429bed3d420243f5aa6
            Return:
                If record is successfully deleted then it will return {'success':'Records Successfully Deleted 59'}

            QueryString for Delete multiple records:
                localhost:8069/api/product.product/unlink/?token=24e635ff9cc74429bed3d420243f5aa6&unlink_ids=[60,61]
            Return:
                If record is successfully deleted then it will return {'success':'Records Successfully Deleted [60,61]'}

        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                try:
                    if Model.browse(id).unlink():
                        return {'success': _('Records Successfully Deleted ID - %d' % id)}
                except Exception as e:
                    return {'error': _('Model Not Found %s' % e)}
            else:
                try:
                    ids_list = post.get('unlink_ids') and eval(
                        post['unlink_ids']) or []
                    if Model.browse(ids_list).unlink():
                        return {'success': _('Records Successfully Deleted %s' % post['unlink_ids'])}
                except Exception as e:
                    return json.dumps({'error': _(' %s' % e)})

    @http.route(['/smerp/api/<string:model>/<int:id>/method/<string:method_name>'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def api_method_call(self, model=None, id=None, method_name=None, **post):
        """
            For calling a method of any model , it is medetory to pass model name, record id and method name
            method call based on odoo8 api standards.
            so no need to pass cr,uid,ids,context as method argument. Other then this argument pass as 'args'=[arg1,arg2] in query string
            eg.
            QueryString for calling a method without argument:
                localhost:8069/api/sale.order/26/method/action_button_confirm/?token=1ec448c54a004165b4c0da976b227260
            Return:
                {"success": "True"}
                It will return dictionary its key 'success' and  and its value will be return as per method calling

            QueryString for calling method with arguments:
                'def get_salenote(self, cr, uid, ids, partner_id, context=None)'
                this method if of sale order for calling this method we need to pass partner_id in args

                localhost:8069/api/sale.order/35/method/get_salenote/?token=1ec448c54a004165b4c0da976b227260&args=[3]

            Return:
                {"success": "sale note"}

            QueryString for calling method with keyword argument
                localhost:8069/api/sale.order/33/method/action_invoice_create/?token=1ec448c54a004165b4c0da976b227260&kwargs={'date_invoice':'2016-09-02'}
            It will return
                {"success": "12"}
        """
        current_user = False
        if post.get('token'):
            current_user = request.env['res.users'].sudo().search(
                [('token', '=', post.get('token'))])
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            try:
                record = Model.browse(id)
                args = []
                kwargs = {}
                if 'args' in post.keys():
                    args = eval(post['args'])
                if 'kwargs' in post.keys():
                    kwargs = eval(post['kwargs'])
                result = getattr(record, method_name)(*args, **kwargs)
                return {'success': _('%s' % result)}
            except Exception as e:
                return {'error': _('%s' % e)}

    def parse_datetime(self, result):
        for data in result:
            for key, value in data.items():
                if isinstance(value, datetime.date):
                    data[key] = odoo_fields.Date.to_string(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = odoo_fields.Datetime.to_string(value)
        return result

    def parse_image(self, result):
        for data in result:
            for key, value in data.items():
                if isinstance(value, bytes):
                    data[key] = value.decode('utf-8')
        return result
