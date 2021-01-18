# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class OpenBalance(models.Model):
    _name = 'partner.open.balance'
    _rec_name = 'reference'

    @api.depends('paid_amount', 'total_amount')
    def _compute_amount(self):
        for rec in self:
            rec.to_pay_amount = rec.total_amount - rec.paid_amount
            if (rec.total_amount == rec.paid_amount):
                rec.status = "paid"

    reference = fields.Char(string="Reference")
    date = fields.Date(string="Date")
    partner_id = fields.Many2one("res.partner")
    paid_amount = fields.Float(string="Paid amount")
    total_amount = fields.Float(string="Total Due amount")
    to_pay_amount = fields.Float(string="To Pay amount", compute="_compute_amount")
    payment_ids = fields.One2many("account.payment", "open_balance_ids")
    move_line_id = fields.Many2one("account.move.line")
    status = fields.Selection([
        ('open', 'Open'),
        ('paid', 'Paid')
    ], default='open', string='status')


class ResPartner(models.Model):
    _inherit = "res.partner"

    open_balance_ids = fields.One2many("partner.open.balance", "partner_id")
    open_balance_amount = fields.Float(string="Total", compute="_compute_balance")

    @api.depends('open_balance_ids')
    def _compute_balance(self):
        self.open_balance_amount = 0
        amount = 0
        for rec in self.open_balance_ids:
            if rec.status != "paid":
                amount = amount + rec.to_pay_amount
        self.open_balance_amount = amount

    def generate_open_bal_partner(self):
        """ Generate the open bal entry for partner """
        if self.open_balance_ids:
            for rec in self.open_balance_ids:
                today = datetime.today().date()
                month = self.company_id.fiscalyear_last_month if self.company_id.fiscalyear_last_month else 1
                opening_date = today.replace(month=int(month), day=31) + timedelta(days=1)
                if opening_date > today:
                    opening_date = opening_date + relativedelta(years=-1)
                if not rec.move_line_id and rec.status=="open":
                    print(self.env.company.id)
                    default_journal = self.env['account.journal'].search(
                        [('type', '=', 'general'), ('company_id', '=', self.env.company.id)], limit=1)
                    recev_default_account = self.env['ir.property'].get('property_account_receivable_id', 'res.partner')
                    payable_default_account = self.env['ir.property'].get('property_account_payable_id', 'res.partner')
                    balancing_account = self.env.company.get_unaffected_earnings_account()
                    partner_account_id = recev_default_account
                    debit_amount = 0
                    credit_amount = 0
                    if self.supplier_rank:
                        partner_account_id = payable_default_account
                        account_opening_move = self.env['account.move'].create({
                            "journal_id": default_journal.id,
                            "ref": "Open Balance Entry",
                            "date": opening_date,
                            "is_openbalance_view": True,
                            'line_ids': [
                                (0, 0, {
                                    'name': ('Automatic Balancing Line'),
                                    'account_id': balancing_account.id,
                                    'debit': rec.to_pay_amount,
                                    'credit':0,
                                }),
                                (0, 0, {
                                    'name': ('Open balanace for Creditors Line'),
                                    'account_id': partner_account_id.id,
                                    'partner_id': self.id,
                                    'debit': 0,
                                    'credit': rec.to_pay_amount,
                                })
                            ]
                        })
                    else:
                        account_opening_move = self.env['account.move'].create({
                            "journal_id": default_journal.id,
                            "ref":"Open Balance Entry",
                            "date":opening_date,
                            "is_openbalance_view": True,
                            'line_ids': [
                                (0, 0, {
                                    'name': ('Automatic Balancing Line'),
                                    'account_id': balancing_account.id,
                                    'debit': 0 ,
                                    'credit': rec.to_pay_amount,
                                }),
                                (0, 0, {
                                    'name': ('Opening Balance for Debtors Line'),
                                    'account_id': partner_account_id.id,
                                    'partner_id': self.id,
                                    'debit': rec.to_pay_amount,
                                    'credit': 0,
                                })
                            ]
                        })
                    account_opening_move.action_post()
                    line_id = account_opening_move.line_ids.filtered(lambda c: c.partner_id and (
                            c.account_id.id ==partner_account_id.id))
                    rec.write({"move_line_id": line_id.id})
