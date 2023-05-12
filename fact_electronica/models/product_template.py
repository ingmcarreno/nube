# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    unidad_sin = fields.Selection(selection=[('2', 'BALDE'),
                                        ('4', 'BOLSA'),
                                        ('6', 'CAJA'),
                                        ('43', 'PAR'),
                                        ('47', 'PIEZAS'),
                                        ('57', 'UNIDAD (BIENES)')],
                             string='Unidad SIN',
                             default='47',
                             index=True)
    cod_sin = fields.Char(string='Codigo producto SIN', default="611629")
    actividad_sin = fields.Char(string='Actividad SIN', default="466300")
