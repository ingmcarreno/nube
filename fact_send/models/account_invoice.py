from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    cod_recepcion = fields.Char('Codigo Recepcion')
    estado_emision = fields.Char('Estado emision')
    fecha_emision = fields.Char('Fecha emision')
    cuf = fields.Char('CUF')
    cuis = fields.Char('CUIS', default='_')
    cufd = fields.Char('CUFD')
    codigo_control = fields.Char('codigo_control')
    link_qr = fields.Char('Link QR')
    codigo_error = fields.Char('Codigo Error')
    mensaje_respuesta = fields.Char('Mensaje respuesta')

    def post_electronic_invoice(self):
        self.ensure_one()
        server_dom = [
            ('state', '=', 'enable')
        ]
        siat_server = self.env['siat.server'].search(server_dom, limit=1)
        if siat_server.id is False:
            raise ValidationError(_('An enabled sever is required'))
        response = siat_server.post_invoice(self)
        if response.status_code not in [200, 201, 202]:
            _logger.info(response.content)
            raise ValidationError(_('Could not validate server response'))
        rjson = json.loads(response.content)
        _logger.info(rjson)
        self.write({
            "cod_recepcion": rjson["codigoRecepcion"],
            "estado_emision": rjson["estadoEmisionEDOC"],
            "fecha_emision": rjson["fechaEmision"] if rjson["fechaEmision"] is not None else False,
            "cuf": rjson["cuf"],
            "cuis": rjson["cuis"],
            "cufd": rjson["cufd"],
            "codigo_control": rjson["codigoControl"],
            "link_qr": rjson["linkCodigoQR"],
            "codigo_error": rjson["codigoError"],
            "mensaje_respuesta": rjson["mensajeRespuesta"]
        })
