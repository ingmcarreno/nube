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
    rememberMe = fields.Boolean('Recordarme', default=True)
    use_root = fields.Boolean('Use root address', default=True)
    service_id = fields.Char('Service ID')
    url_root = fields.Char('Server root URL')
    url_endpoints = fields.Text('Enpoints', help='dictionary', default="""{
        'auth': 'api/authenticate',
        'cancel': '/api/integrations/cancel',
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
        headers = self.get_default_headers()
        data = {'username': self.user_login,
               'rememberMe': self.rememberMe,
               'password': self.password,}
        response = requests.get(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            result = response.json()            
            now = datetime.now()
            validity_date = datetime.strptime(str(now), "%Y-%m-%d %H:%M:%S.%f")
            validity_date = validity_date + timedelta(days=30)
            validity_date = str(validity_date)
            validity_date = validity_date.replace(' ', 'T')
            validity_date = validity_date[:23]
            self.write({
                'token': result['id_token'],
                'validity': validity_date
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
        if self.id_token != '':
            headers.update({'Authorization': 'Bearer %s' % self.id_token})
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
        invoice_date = invoice_date + 'Z'
        headers = self.get_default_headers()
        data = {
            "id": invoice.id,
            "extraCustomerAddress": invoice.direccion,
            "additionalDiscount": 0,
            "name": invoice.partner_id.name,
            "documentTypeCode": invoice.tipo_documento,
            "documentNumber": invoice.nit,
            "customerCode": str(invoice.partner_id.ref),
            "emissionDate": invoice_date,
            "branchId": invoice.cod_sucursal,
            "branchNumber": invoice.cod_puntoventa,
            "invoiceNumber": invoice.number,
            "emailNotification": invoice.partner_id.email,
            "currencyIso": invoice.tipo_moneda,
            "exchangeRate": invoice.tipo_cambio,
            "paymentMethodType": invoice.metodo_pago,
            "userCode": invoice.create_uid.name,
            "details": [
                {
                    "productCode": str(l.product_id.barcode),
                    "concept": l.product_id.name,
                    "quantity": l.quantity,
                    "unitPrice": l.price_unit,
                    "discountAmount": (l.price_unit * l.discount)/100,
                    "subtotal": (l.price_unit * l.quantity) - ((l.price_unit * l.discount)/100),
                } for l in invoice.invoice_line_ids
            ]
        }
        _logger.info(data)
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response
    
    
    def cancel_invoice_siat(self, invoice):
        self.validate_token()
        url_base = self.url_root if self.use_root is True else ''
        endpoints = eval(self.url_endpoints)
        end_point = endpoints.get('cancel', '/api/integrations/cancel')
        url = url_base + end_point
        siatReason = '1'
        invoiceType = 'WEB'
        headers = self.get_default_headers()
        data = {
            "cuf": invoice.cuf,
            "invoiceType": invoiceType,
            "siatReason": siatReason,
        }
        _logger.info(data)
        response = requests.put(url, data=json.dumps(data), headers=headers)
        return response
