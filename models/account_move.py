from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        res = super().write(vals)
        if 'payment_state' in vals and vals['payment_state'] in ('paid', 'in_payment'):
            self._sync_sale_invoice_state()
        return res

    def _sync_sale_invoice_state(self):
        """When invoice is paid, mark related SOs as paid and unblock partner if safe."""
        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            sale_orders = self.env['sale.order'].search([
                ('invoice_ids', 'in', [move.id]),
                ('invoice_state', 'not in', ('paid',)),
            ])
            if not sale_orders:
                continue
            sale_orders.write({'invoice_state': 'paid'})
            for partner in sale_orders.mapped('partner_id'):
                still_blocked = self.env['sale.order'].search([
                    ('partner_id', '=', partner.id),
                    ('invoice_state', '=', 'blocked'),
                ], limit=1)
                if not still_blocked:
                    partner.is_blocked = False
