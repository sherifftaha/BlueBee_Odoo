from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta
from urllib.parse import quote


MIN_PIECES = 6
FEE_PER_PIECE = 25.0
FEE_PRODUCT_XMLID = 'invoice_deadline.product_below_min_fee'


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_open_date = fields.Datetime(
        string='Invoice Open Date',
        readonly=False,  # TEMP: made editable for demo — revert to readonly=True after demo
        copy=False,
    )
    invoice_deadline_date = fields.Datetime(
        string='Invoice Deadline Date',
        compute='_compute_invoice_dates',
        store=True,
    )
    grace_end_date = fields.Datetime(
        string='Grace End Date',
        compute='_compute_invoice_dates',
        store=True,
    )
    invoice_state = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('locked', 'Locked - Awaiting Payment'),
            ('grace', 'Grace Period'),
            ('blocked', 'Blocked'),
            ('paid', 'Paid'),
        ],
        string='Invoice State',
        default='open',
        copy=False,
    )
    merged_into_so_id = fields.Many2one(
        'sale.order',
        string='Merged Into Order',
        readonly=True,
        copy=False,
        help='This order was merged into the existing open order.',
    )
    can_use_continuation = fields.Boolean(
        string='Can Use Continuation',
        compute='_compute_can_use_continuation',
    )

    total_pieces = fields.Float(
        string='Total Pieces',
        compute='_compute_total_pieces',
        help='Sum of qty across all order lines (excluding the surcharge line).',
    )
    is_below_minimum = fields.Boolean(
        string='Below Minimum (6 pieces)',
        compute='_compute_total_pieces',
    )
    minimum_fee_amount = fields.Float(
        string='Below-minimum Surcharge',
        compute='_compute_total_pieces',
    )

    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_total_pieces(self):
        fee_pid = self._get_fee_product_id()
        for order in self:
            non_fee = order.order_line.filtered(lambda l: l.product_id.id != fee_pid)
            pieces = sum(non_fee.mapped('product_uom_qty'))
            order.total_pieces = pieces
            order.is_below_minimum = 0 < pieces < MIN_PIECES
            order.minimum_fee_amount = pieces * FEE_PER_PIECE if order.is_below_minimum else 0.0

    @api.model
    def _get_fee_product_id(self):
        product = self.env.ref(FEE_PRODUCT_XMLID, raise_if_not_found=False)
        if not product:
            return False
        return product.product_variant_id.id

    def _recompute_minimum_surcharge(self):
        """Add/update/remove the below-minimum surcharge line on this order.

        Applies only to OPEN (confirmed but not yet locked) invoices.
        Cart (draft) is skipped — surcharge belongs on the actual invoice, not the cart.
        Locked / grace / blocked / paid are frozen.
        """
        fee_pid = self._get_fee_product_id()
        if not fee_pid:
            return
        for order in self:
            if order.state not in ('sale', 'done'):
                continue
            if order.invoice_state != 'open':
                continue

            surcharge_lines = order.order_line.filtered(lambda l: l.product_id.id == fee_pid)
            non_fee_lines = order.order_line - surcharge_lines
            pieces = sum(non_fee_lines.mapped('product_uom_qty'))

            if 0 < pieces < MIN_PIECES:
                fee_amount = pieces * FEE_PER_PIECE
                description = (
                    "رسوم أقل من الحد الأدنى (أقل من 6 قطع)\n"
                    "Below-minimum fee (order under 6 pieces)"
                )
                vals = {
                    'product_uom_qty': pieces,
                    'price_unit': FEE_PER_PIECE,
                    'name': description,
                    'sequence': 9999,
                }
                if surcharge_lines:
                    # Keep the first, zero out duplicates (defensive)
                    keeper = surcharge_lines[0]
                    extras = surcharge_lines - keeper
                    if extras:
                        extras.with_context(skip_min_surcharge=True).write({
                            'product_uom_qty': 0.0,
                            'price_unit': 0.0,
                            'sequence': 9999,
                        })
                    keeper.with_context(skip_min_surcharge=True).write(vals)
                else:
                    self.env['sale.order.line'].with_context(skip_min_surcharge=True).create({
                        'order_id': order.id,
                        'product_id': fee_pid,
                        'product_uom_qty': pieces,
                        'price_unit': FEE_PER_PIECE,
                        'name': description,
                        'sequence': 9999,
                    })
            else:
                # Pieces >= 6 (or 0): zero out the surcharge line.
                # Cannot unlink lines on confirmed orders — zero them out instead.
                if surcharge_lines:
                    surcharge_lines.with_context(skip_min_surcharge=True).write({
                        'product_uom_qty': 0.0,
                        'price_unit': 0.0,
                        'sequence': 9999,
                    })

    @api.depends('invoice_open_date')
    def _compute_invoice_dates(self):
        for order in self:
            if order.invoice_open_date:
                order.invoice_deadline_date = order.invoice_open_date + timedelta(days=10)
                order.grace_end_date = order.invoice_open_date + timedelta(days=16)
            else:
                order.invoice_deadline_date = False
                order.grace_end_date = False

    @api.depends('invoice_state', 'partner_id', 'partner_id.has_used_continuation',
                 'order_line.product_uom_qty')
    def _compute_can_use_continuation(self):
        for order in self:
            if order.invoice_state != 'locked' or order.partner_id.has_used_continuation:
                order.can_use_continuation = False
                continue
            partner_orders = self.search([
                ('partner_id', '=', order.partner_id.id),
                ('invoice_state', 'in', ('open', 'locked')),
                ('state', 'in', ('sale', 'done')),
            ])
            fee_pid = self._get_fee_product_id()
            total_qty = sum(
                l.product_uom_qty
                for so in partner_orders
                for l in so.order_line
                if l.product_id.id != fee_pid and l.product_uom_qty > 0
            )
            order.can_use_continuation = total_qty < 20

    def action_continuation(self):
        self.ensure_one()
        partner = self.partner_id

        if self.invoice_state != 'locked':
            raise UserError("الاستكمال متاح فقط للفواتير المقفلة.")

        if partner.has_used_continuation:
            raise UserError("تم استخدام خيار الاستكمال مسبقاً لهذا الحساب. لا يمكن استخدامه مجدداً.")

        partner_orders = self.search([
            ('partner_id', '=', partner.id),
            ('invoice_state', 'in', ('open', 'locked')),
            ('state', 'in', ('sale', 'done')),
        ])
        fee_pid = self._get_fee_product_id()
        total_qty = sum(
            l.product_uom_qty
            for so in partner_orders
            for l in so.order_line
            if l.product_id.id != fee_pid and l.product_uom_qty > 0
        )
        if total_qty >= 20:
            raise UserError(
                f"إجمالي الطلبات المفتوحة {int(total_qty)} قطعة. "
                "الاستكمال متاح فقط لمن لديه أقل من 20 قطعة."
            )

        # Merge all other open/locked SOs into this one
        other_orders = partner_orders - self
        if other_orders:
            for other in other_orders:
                lines_to_move = other.order_line.filtered(
                    lambda l: l.product_id.id != fee_pid
                )
                lines_to_move.with_context(skip_min_surcharge=True).write({'order_id': self.id})
                other.write({'merged_into_so_id': self.id})
            other_orders.action_cancel()
            other_orders.unlink()

        # Reset this SO back to open with a fresh countdown
        self.write({
            'invoice_open_date': fields.Datetime.now(),
            'invoice_state': 'open',
        })
        partner.write({'has_used_continuation': True})
        self._recompute_minimum_surcharge()

    def _cron_update_invoice_states(self):
        now = fields.Datetime.now()

        # open → locked after 10 days
        open_orders = self.search([
            ('invoice_state', '=', 'open'),
            ('invoice_deadline_date', '!=', False),
            ('invoice_deadline_date', '<=', now),
        ])
        open_orders.write({'invoice_state': 'locked'})

        # locked/grace → blocked after 16 days
        # Only the overdue SO itself changes to 'blocked'.
        # Other SOs for the same partner keep their own states — the partner-level
        # is_blocked flag is enough to prevent shop access.
        escalate_orders = self.search([
            ('invoice_state', 'in', ('locked', 'grace')),
            ('grace_end_date', '!=', False),
            ('grace_end_date', '<=', now),
        ])
        if escalate_orders:
            partners = escalate_orders.mapped('partner_id')
            escalate_orders.write({'invoice_state': 'blocked'})
            partners.write({'is_blocked': True})

    def action_confirm(self):
        # Block if customer is blocked
        for order in self:
            if order.partner_id.is_blocked:
                raise UserError(
                    "حسابك محظور بسبب فواتير غير مدفوعة. "
                    "Your account is blocked due to unpaid invoices. "
                    "Please contact us to resolve."
                )

        # Unified invoice: merge into existing open SO if one exists
        to_confirm = self.env['sale.order']
        to_delete = self.env['sale.order']
        merge_target_id = None  # existing SO id to redirect to after merge

        for order in self:
            existing = self.search([
                ('partner_id', '=', order.partner_id.id),
                ('invoice_state', '=', 'open'),
                ('state', 'in', ('sale', 'done')),
                ('id', '!=', order.id),
            ], limit=1)
            if existing:
                order.order_line.write({'order_id': existing.id})
                merge_target_id = existing.id
                to_delete |= order
            else:
                to_confirm |= order

        # Cancel then permanently delete the empty merged orders
        if to_delete:
            to_delete.action_cancel()
            to_delete.unlink()

        if to_confirm:
            res = super(SaleOrder, to_confirm).action_confirm()
        else:
            res = True

        # Set invoice_open_date on freshly confirmed orders
        for order in to_confirm:
            if not order.invoice_open_date:
                order.invoice_open_date = fields.Datetime.now()

        # Recompute below-minimum surcharge on the now-open invoices
        if to_confirm:
            to_confirm._recompute_minimum_surcharge()
        if merge_target_id:
            self.browse(merge_target_id)._recompute_minimum_surcharge()

        # If everything was merged (nothing newly confirmed), redirect to existing SO
        if merge_target_id and not to_confirm:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': merge_target_id,
                'view_mode': 'form',
                'target': 'current',
            }

        return res

    def action_mark_paid(self):
        """Manual: admin marks SO as paid then re-evaluates partner block status.

        After paying, any sibling SOs that were cascade-blocked (grace not yet
        expired) are restored to their natural state from their own dates.
        Partner is unblocked only if no SOs remain genuinely overdue.
        """
        now = fields.Datetime.now()
        for order in self:
            order.invoice_state = 'paid'
            partner = order.partner_id

            # Find all OTHER blocked SOs for this partner
            other_blocked = self.search([
                ('partner_id', '=', partner.id),
                ('invoice_state', '=', 'blocked'),
                ('id', '!=', order.id),
            ])

            # Restore any that were cascade-blocked (grace hasn't actually expired)
            for sibling in other_blocked:
                if sibling.grace_end_date and sibling.grace_end_date > now:
                    # Grace period not yet expired — restore natural state
                    if sibling.invoice_deadline_date and sibling.invoice_deadline_date <= now:
                        sibling.invoice_state = 'locked'
                    else:
                        sibling.invoice_state = 'open'

            # Re-check: unblock partner only if no genuinely overdue SOs remain
            genuinely_blocked = self.search([
                ('partner_id', '=', partner.id),
                ('invoice_state', '=', 'blocked'),
                ('id', '!=', order.id),
            ], limit=1)
            if not genuinely_blocked:
                partner.is_blocked = False

    def action_unmark_paid(self):
        """Reverse Mark as Paid: recompute state based on current dates."""
        now = fields.Datetime.now()
        for order in self:
            if order.invoice_state != 'paid':
                continue
            if not order.invoice_open_date:
                order.invoice_state = 'open'
                continue
            if order.grace_end_date and order.grace_end_date <= now:
                order.invoice_state = 'blocked'
                order.partner_id.is_blocked = True
            elif order.invoice_deadline_date and order.invoice_deadline_date <= now:
                order.invoice_state = 'locked'
            else:
                order.invoice_state = 'open'

    def _get_order_lines_to_report(self):
        """Hide the below-minimum fee line when it has been zeroed out (qty=0)."""
        lines = super()._get_order_lines_to_report()
        fee_pid = self._get_fee_product_id()
        if not fee_pid:
            return lines
        return lines.filtered(
            lambda l: not (l.product_id.id == fee_pid and l.product_uom_qty == 0)
        )

    def _is_payment_overdue(self):
        """True when the original 10-day deadline has passed."""
        self.ensure_one()
        if not self.invoice_deadline_date:
            return False
        return self.invoice_deadline_date <= fields.Datetime.now()

    def _get_payment_info(self):
        """Return payment instructions dict (used by portal template)."""
        self.ensure_one()
        ICP = self.env['ir.config_parameter'].sudo()
        return {
            'vodafone_cash': ICP.get_param('invoice_deadline.vodafone_cash', ''),
            'postal_account': ICP.get_param('invoice_deadline.postal_account', ''),
            'whatsapp_phone': ICP.get_param('invoice_deadline.whatsapp_phone', ''),
        }

    def _get_whatsapp_payment_url(self):
        """Build a wa.me URL with a pre-filled payment-confirmation message."""
        self.ensure_one()
        phone = self._get_payment_info().get('whatsapp_phone')
        if not phone:
            return False
        currency = self.currency_id.symbol or self.currency_id.name or 'EGP'
        lines = [
            "السلام عليكم",
            f"العميل: {self.partner_id.name}",
            f"رقم الفاتورة: {self.name}",
            f"المبلغ: {self.amount_total:.2f} {currency}",
            "رقم عملية التحويل: ___",
            "طريقة الدفع (فودافون كاش / بريد): ___",
        ]
        return "https://wa.me/%s?text=%s" % (phone, quote("\n".join(lines)))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        if not self.env.context.get('skip_min_surcharge'):
            lines.mapped('order_id')._recompute_minimum_surcharge()
        return lines

    def write(self, vals):
        # If lines are moving to a different order (cart→open invoice merge),
        # we need to recompute on the OLD order too — but in our merge flow the
        # source cart is deleted right after, so it's enough to recompute on the
        # post-write order (the merge target).
        res = super().write(vals)
        if not self.env.context.get('skip_min_surcharge') and (
            'product_uom_qty' in vals or 'product_id' in vals or 'order_id' in vals
        ):
            self.mapped('order_id')._recompute_minimum_surcharge()
        return res

    def unlink(self):
        orders = self.mapped('order_id')
        skip = self.env.context.get('skip_min_surcharge')
        res = super().unlink()
        if not skip:
            orders.exists()._recompute_minimum_surcharge()
        return res
