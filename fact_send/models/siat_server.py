from odoo import models, fields, api, _
import requests
import json
from datetime import timedelta, datetime
import logging

_logger = logging.getLogger(__name__)


class SIATServer(models.Model):
    _name = 'siat.server'
    _description = 'Server link settings'

    environment = fields.Selection([
        ('test', 'Tests & pilot'),
        ('prod', 'Production')
    ], string='Environment', default='test')

    name = fields.Char('Name Reference')
    user_login = fields.Char('User')
    user_password = fields.Char('Password')
    use_root = fields.Boolean('Use root address', default=True)
    service_id = fields.Char('Service ID')
    url_root = fields.Char('Server root URL')
    url_endpoints = fields.Text('Enpoints', help='dictionary', default="""{
        'auth': 'account/authenticate',
        'cancel': 'cancel',
        'compraventa': '',
    }""")
    token = fields.Char('Token', default='')
    state = fields.Selection(
        [
            ('enable', 'Enabled'),
            ('disable', 'Disabled')
        ], string="State", default='enable')
    validity = fields.Datetime('Validity')

    def auth_service(self):
        self.ensure_one()
        endpoints = eval(self.url_endpoints)
        url = endpoints.get('auth', '/auth')
        credentials = (self.user_login, self.user_password)
        params = {'Id': self.service_id}
        response = requests.get(url, params=params, auth=credentials)
        if response.status_code == 200:
            result = response.json()
            sp_date = result['expira'].split('T')
            str_date = '%s %s' % (sp_date[0], sp_date[1][:8])
            expiration = fields.datetime.strptime(
                str_date, '%Y-%m-%d %H:%M:%S')
            self.write({
                'token': result['token'],
                'validity': expiration + timedelta(hours=4)
            })
            return True
        raise UserWarning(_('could not authenticate'))

    def set_enable(self):
        for record in self:
            record.state = 'enable'

    def set_disable(self):
        for record in self:
            record.state = 'disable'

    def get_default_headers(self):
        headers = {
            'Content-type': 'application/json',
        }
        if self.token != '':
            headers.update({'Authorization': 'Bearer %s' % self.token})
        return headers

    def validate_token(self):
        if self.validity is False:
            self.auth_service()
        validity = self.validity
        if isinstance(validity, (str)):
            validity = datetime.strptime(validity, '%Y-%m-%d %H:%M:%S')
        now = fields.datetime.now()
        if isinstance(now, (str)):
            now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        if validity <= now:
            self.auth_service()

    def post_invoice(self, invoice):
        self.validate_token()
        url_base = self.url_root if self.use_root is True else ''
        endpoints = eval(self.url_endpoints)
        end_point = endpoints.get('compraventa', '/invoice/create')
        url = url_base + end_point
        now = datetime.now()
        invoice_date = datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")
        invoice_date = invoice_date + timedelta(hours=-4)
        invoice_date = str(invoice_date)
        invoice_date = invoice_date.replace(' ', 'T')
        invoice_date = invoice_date[:23]        
        headers = self.get_default_headers()
        data = {
            "NitEmisor": invoice.nit_empresa,
            "RazonSocialEmisor": invoice.razon,
            "Municipio": invoice.sucursal,
            "Direccion": invoice.direccion,
            "Telefono": invoice.company_id.phone or None,
            "NombreRazonSocial": invoice.partner_id.name,
            "CodigoTipoDocumentoIdentidad": invoice.tipo_documento,
            "NumeroDocumento": invoice.nit,
            "CodigoCliente": str(invoice.partner_id.ref),
            "FechaEmision": invoice_date,
            "CodigoSucursal": invoice.cod_sucursal,
            "CodigoPuntoVenta": invoice.cod_puntoventa,
            "NumeroFactura": invoice.number,
            "MontoTotal": invoice.amount_total_sin,
            "MontoTotalSujetoIva": invoice.amount_total_sin,
            "CodigoMoneda": invoice.tipo_moneda,
            "TipoCambio": invoice.tipo_cambio,
            "MontoTotalMoneda": invoice.amount_total_sin,
            "CodigoMetodoPago": invoice.metodo_pago,
            "Leyenda": invoice.leyenda,
            "TipoEmision": 1,
            "Usuario": str(invoice.tipo_cambio),
            "NombreIntegracion": invoice.integracion,
            "Detalles": [
                {
                    "ActividadEconomica": l.actividad_sin,
                    "CodigoProductoSin": int(l.cod_sin),
                    "CodigoProducto": str(l.product_id.barcode),
                    "Descripcion": l.product_id.name,
                    "UnidadMedida": int(l.unidad_sin),
                    "Cantidad": l.quantity,
                    "PrecioUnitario": l.price_net_sin,
                    "MontoDescuento": 0,
                    "SubTotal": l.price_subtotal_sin,
                } for l in invoice.invoice_line_ids
            ]
        }
        _logger.info(data)
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response
