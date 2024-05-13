from odoo import models, fields, exceptions
from odoo.exceptions import UserError

class AccountAnalyticLineExtend(models.Model):
    _inherit = 'account.analytic.line'

    confirmed_line = fields.Boolean(string='Confirmar Línea Analítica',default=False)

    def button_in_progress(self):
        if self.account_id.name != 'Sin asignar':
            self.sudo().confirmed_line = True
        else:
            raise UserError('Debes seleccionar un empleado')
    def button_edit(self):
        self.sudo().confirmed_line = False

