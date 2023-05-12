# -*- coding: utf-8 -*-
from odoo import models, fields

class res_partner(models.Model):
    _inherit = "res.partner"

    tipo_documento = fields.Selection(selection=[('1', 'CI - CEDULA DE IDENTIDAD'),
                                        ('2', 'CEX - CEDULA DE IDENTIDAD DE EXTRANJERO'),
                                        ('3', 'PAS - PASAPORTE'),
                                        ('4', 'OD - OTRO DOCUMENTO DE IDENTIDAD'),
                                        ('5', 'NIT - NÚMERO DE IDENTIFICACIÓN TRIBUTARIA')],
                             string='Tipo de Documento',
                             default='5',
                             index=True)

