from odoo import fields, http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInvoiceDeadline(WebsiteSale):

    def _bb_is_public(self):
        """Return True if the visitor is not logged in (anonymous)."""
        return request.env.user._is_public()

    def _bb_is_blocked(self):
        """Return True if logged-in user is a blocked partner."""
        user = request.env.user
        if user._is_public():
            return False
        return user.partner_id.sudo().is_blocked

    def _bb_clear_cart_session(self):
        """Wipe all cart-related session keys so the navbar badge resets."""
        for key in ('sale_order_id', 'website_sale_cart_quantity',
                    'website_sale_current_pl', 'website_sale_carrier_recompute'):
            request.session.pop(key, None)

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        if self._bb_is_public():
            return request.redirect('/web/login')
        if self._bb_is_blocked():
            return request.redirect('/shop/blocked')
        return super().shop(page=page, category=category, search=search,
                            min_price=min_price, max_price=max_price, ppg=ppg, **post)

    @http.route()
    def cart(self, **post):
        if self._bb_is_public():
            return request.redirect('/web/login')
        if self._bb_is_blocked():
            return request.redirect('/shop/blocked')
        return super().cart(**post)

    @http.route()
    def checkout(self, **post):
        if self._bb_is_public():
            return request.redirect('/web/login')
        if self._bb_is_blocked():
            return request.redirect('/shop/blocked')
        return super().checkout(**post)

    @http.route()
    def confirm_order(self, **post):
        """Replace the normal pay-on-confirm flow.
        Behaviour:
        - If customer has an existing open/locked/grace SO → move our cart lines
          into it, delete the cart, redirect to the merged SO.
        - Otherwise → confirm the cart as a fresh invoice (state=sale,
          invoice_state=open) and redirect to it.
        Either way: skip /shop/payment entirely. Payment is a separate explicit
        action via the Pay Now button on the portal SO page.
        """
        if self._bb_is_public():
            return request.redirect('/web/login')
        if self._bb_is_blocked():
            return request.redirect('/shop/blocked')

        order = request.website.sale_get_order()
        if not order or not order.order_line:
            return request.redirect('/shop/cart')

        # Need sudo to read partner / mutate other partner's SO
        order_sudo = order.sudo()
        partner = order_sudo.partner_id

        # Only merge into OPEN invoices. 'locked' invoices were intentionally
        # closed by the customer (Pay & Close) — new items must start a fresh SO.
        existing_so = request.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('invoice_state', '=', 'open'),
            ('state', 'in', ('sale', 'done')),
            ('id', '!=', order_sudo.id),
        ], limit=1)

        if existing_so:
            # Merge: move lines, delete new cart SO
            order_sudo.order_line.write({'order_id': existing_so.id})
            order_sudo.action_cancel()
            order_sudo.unlink()
            self._bb_clear_cart_session()
            return request.redirect('/my/orders/%d?invoice_added=1' % existing_so.id)

        # No existing invoice: confirm this cart as a new one.
        order_sudo.action_confirm()
        if not order_sudo.invoice_open_date:
            order_sudo.invoice_open_date = fields.Datetime.now()

        new_id = order_sudo.id
        self._bb_clear_cart_session()
        return request.redirect('/my/orders/%d?invoice_added=1' % new_id)


class BlockedAccountController(http.Controller):

    @http.route('/shop/blocked', type='http', auth='public', website=True, sitemap=False)
    def blocked_page(self, **kw):
        return request.render('invoice_deadline.blocked_account_page')


class CloseInvoiceController(http.Controller):

    @http.route('/my/orders/<int:order_id>/close_for_payment',
                type='http', auth='user', website=True, methods=['POST'], csrf=True)
    def close_for_payment(self, order_id, **kw):
        """Customer-initiated lock: open → locked.
        After locking, no more items can be merged into this SO; the WhatsApp
        payment-proof button becomes available on the portal SO page.
        """
        Order = request.env['sale.order'].sudo()
        order = Order.browse(order_id)
        if not order.exists():
            return request.redirect('/my/orders')
        if order.partner_id.id != request.env.user.partner_id.id:
            return request.redirect('/my/orders')
        if order.invoice_state == 'open':
            order.invoice_state = 'locked'
        return request.redirect('/my/orders/%d' % order_id)
