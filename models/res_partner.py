from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blocked = fields.Boolean(
        string='Blocked - Unpaid Invoices',
        default=False,
        copy=False,
    )
