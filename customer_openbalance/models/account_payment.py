# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Payment(models.Model):
    _inherit = "account.payment"

    open_balance_ids = fields.Many2one("partner.open.balance", domain="[('state', '=', 'open')]")

    open_balance_amount = fields.Float(string="Open Balance amount")
    payment_level = fields.Selection([('direct', "Direct"), ('open_bal', "Open Balance")], default="direct")

    @api.onchange("open_balance_ids")
    def _onchange_open_balance_ids(self):
        """ open_balance_amount  """
        values = []
        open_balance_amount_value = 0
        if self.open_balance_ids:
            self.open_balance_amount = self.open_balance_ids.to_pay_amount

    def post(self):
        res = super(Payment, self).post()
        if self.open_balance_ids:
            debit_move_id = self.open_balance_ids.move_line_id
            pay_line = self.open_balance_ids
            status = "open"
            if pay_line.to_pay_amount > 0:
                paid_amount = self.amount + pay_line.paid_amount
                if (pay_line.total_amount == paid_amount):
                    status = "paid"
                pay_line.write({"paid_amount": paid_amount,
                                "status": status})
            if self.move_line_ids:
                reconcline_lines = self.env["account.partial.reconcile"]
                if self.payment_type=="inbound" and self.partner_type=="customer":
                    move_line = self.move_line_ids.filtered(lambda p: (not p.reconciled) and (p.name == "Customer Payment"))
                    if move_line:
                        vals = {
                            'debit_move_id': debit_move_id.id,
                            'credit_move_id': move_line.id,
                            'amount': self.amount,
                        }
                        reconcline_lines.create(vals)
                    else:
                        return "No move lines to return"
                elif self.payment_type=="outbound" and self.partner_type=="supplier":
                    move_line = self.move_line_ids.filtered(
                        lambda p: (not p.reconciled) and (
                                (p.name == "Vendor Payment") or (p.credit > 0)))
                    if move_line:
                        vals = {
                            'debit_move_id': move_line[0].id,
                            'credit_move_id': debit_move_id.id,
                            'amount': self.amount,
                        }
                        reconcline_lines.create(vals)
                    else:
                        return  "No move lines to return"
        return res
