# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Payment(models.Model):
    _inherit = "account.payment"

    open_balance_ids = fields.Many2many("partner.open.balance", domain="[('state', '=', 'open')]")
    open_balance_amount = fields.Float(string="Open Balance amount")


    @api.onchange("open_balance_ids")
    def _onchange_open_balance_ids(self):
        """ open_balance_amount  """
        values = []
        open_balance_amount_value = 0
        if self.open_balance_ids:
            for rec in self.open_balance_ids:
                open_balance_amount_value += rec.to_pay_amount
                added_line = self.payment_lines.filtered(lambda x: x.open_balance_id == rec.id)
                if not added_line:
                    values.append([0, 0, {
                        'amount_total': rec.total_amount,
                        'pay_amount': 0,
                        'open_balance_id': rec.id,
                    }])
        self.open_balance_amount = open_balance_amount_value
        self.payment_lines = False
        self.payment_lines = values


