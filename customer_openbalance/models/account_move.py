# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import fields, models,api,_
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_openbalance_view = fields.Boolean(string="Open Balance Entry")

