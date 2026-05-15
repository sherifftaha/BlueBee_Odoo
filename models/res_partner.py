from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blocked = fields.Boolean(
        string='Blocked - Unpaid Invoices',
        default=False,
        copy=False,
    )
    has_used_continuation = fields.Boolean(
        string='Used Continuation — استخدم الاستكمال',
        default=False,
        copy=False,
        help='العميل استخدم خيار الاستكمال مرة واحدة ولا يمكنه استخدامه مجدداً.',
    )
