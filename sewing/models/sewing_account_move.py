from odoo import models, fields, exceptions
from odoo.exceptions import UserError

class SewingAccountMove(models.Model):
    _inherit = 'account.move'


    def button_print_ticket(self):
        return self.env.ref('sewing.action_ticket_invoice_report').report_action(self)