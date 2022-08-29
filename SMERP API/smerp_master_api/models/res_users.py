# -*- coding: utf-8 -*-
from pydoc import describe
import uuid
from odoo import fields, models, api
from odoo.osv import expression
from odoo.exceptions import AccessDenied


class SaasPlan(models.Model):
    _inherit = "saas.plan"

    token = fields.Char()
    description = fields.Html('Description')
    price_monthly = fields.Float(string="Price / Month")
    price_yearly = fields.Float(string="Price / Year")