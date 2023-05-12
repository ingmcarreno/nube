# -*- coding: utf-8 -*-
from odoo import models, fields, api

class account_invoice(models.Model):

    _inherit = "account.invoice"
    _order = 'id desc'

    tipo_documento = fields.Selection(related='partner_id.tipo_documento', string="NIT",store=True)
    cod_sucursal = fields.Char('Codigo Sucursal',size=64,help = 'Codigo de sucursal SIN',default='0',readonly=True)
    cod_puntoventa = fields.Char('Codigo de Punto Venta',size=64,help = 'Codigo de punto de venta SIN',default='0',readonly=True)
    tipo_moneda = fields.Selection(selection=[('1', 'BOLIVIANO'),
                                        ('2', 'DOLAR')],
                             string='Moneda SIN',
                             default='1')
    tipo_cambio = fields.Float('Tipo de Cambio',default='1', store=True)
    metodo_pago = fields.Selection(selection=[('1', 'EFECTIVO'),
                                        ('2', 'TARJETA'),
                                        ('3', 'CHEQUE'),
                                        ('4', 'VALES'),
                                        ('5', 'OTROS'),
                                        ('6', 'PAGO POSTERIOR'),
                                        ('7', 'TRANSFERENCIA BANCARIA'),
                                        ('8', 'DEPOSITO EN CUENTA')],
                             string='Metodo de Pago',
                             default='1')
    integracion = fields.Char('Integracion',default='eDoc Gurusoft',store=True,readonly=True)
    amount_total_sin = fields.Float(
        string='Total SIN',
        compute='_compute_sin_prices_and_taxes'
    )

    @api.multi
    @api.depends('invoice_line_ids.price_subtotal_sin')
    def _compute_sin_prices_and_taxes(self):
        self.amount_total_sin = sum(line.price_subtotal_sin for line in self.invoice_line_ids)

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line" 

    unidad_sin = fields.Selection(related='product_id.unidad_sin', string="Unidad",store=True)
    cod_sin = fields.Char(related='product_id.cod_sin', string="Codigo SIN",store=True)
    actividad_sin = fields.Char(related='product_id.actividad_sin', string="Actividad SIN",store=True)
    price_unit_sin = fields.Float(
        string='Precio SIN',
        compute='_compute_report_prices_and_taxes'
    )
    price_subtotal_sin = fields.Float(
        string='Subtotal SIN',
        compute='_compute_report_prices_and_taxes'
    )
    price_net_sin = fields.Float(
        string='Neto SIN',
        compute='_compute_report_prices_and_taxes'
    )

    @api.multi
    @api.depends('price_unit', 'price_subtotal')
    def _compute_report_prices_and_taxes(self):
        for line in self:
            price_unit_sin = line.price_unit            
            price_net_sin = price_unit_sin * (
                1 - (line.discount or 0.0) / 100.0)
            price_net_sin = round(price_net_sin * 6.96, 2)
            price_subtotal_sin = round(price_net_sin * line.quantity, 2)

            line.price_subtotal_sin = price_subtotal_sin
            line.price_unit_sin = price_unit_sin
            line.price_net_sin = price_net_sin