from odoo import _lt, models


class Website(models.Model):
    _inherit = 'website'

    def _get_checkout_step_list(self):
        """Relabel cart/checkout buttons to reflect 'add to invoice' flow."""
        steps = super()._get_checkout_step_list()
        for xmlids, vals in steps:
            if 'website_sale.cart' in xmlids:
                vals['main_button'] = _lt("Add to Invoice")
            elif 'website_sale.checkout' in xmlids or 'website_sale.address' in xmlids:
                vals['main_button'] = _lt("Add to Invoice")
        return steps
