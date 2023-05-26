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

