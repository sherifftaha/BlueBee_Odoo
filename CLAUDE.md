# CLAUDE.md — BlueBee Odoo Project
# مشروع BlueBee على Odoo

---

## 1. ENVIRONMENT — البيئة

| Item | Value |
|------|-------|
| Odoo Version | 17.0 |
| Platform | Docker on Windows 10 |
| docker-compose.yml | `C:\Users\Sherif Taha\Desktop\docker-compose.yml` |
| Odoo modules path | `C:\odoo-modules\` |
| Custom module path | `C:\odoo-modules\invoice_deadline\` |
| DB container | `desktop-db-1` (service name: `db`) |
| Odoo container | `desktop-odoo-1` (service name: `odoo`) |
| Database name | `odoo` |
| DB user | `odoo` |
| DB password | `odoo` |
| DB host (inside docker) | `db` |
| Odoo URL | `http://localhost:8069` |

### Docker Commands
```bash
# Restart Odoo
cd "C:\Users\Sherif Taha\Desktop"
docker compose restart odoo

# Upgrade module
docker compose exec odoo odoo -u invoice_deadline -d odoo --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# Run SQL
docker compose exec db psql -U odoo -d odoo -c "YOUR SQL HERE"

# Odoo shell
docker compose exec odoo odoo shell -d odoo --db_host=db --db_user=odoo --db_password=odoo --no-http
```

---

## 2. BUSINESS CONTEXT — السياق التجاري

**Company:** BlueBee-Eg — ملابس أطفال ومستلزمات بالجملة بالقطعة
**Location:** المنصورة، مصر
**Platform:** Odoo SH (production) — هذا الكود على Odoo Educational للـ demo

### Business Rules — قواعد العمل
- البيع للتجار فقط (B2B) — مش للأفراد
- الموقع مقتصر على التجار المسجلين (invitation only)
- البيع بالقطعة (مش سريهات مغلقة)
- حد أدنى 6 قطع، أقل من 6 بزيادة 25 جنيه للقطعة

### Loyalty System — نظام الولاء
| Level | Discount | Threshold |
|-------|----------|-----------|
| برونزي Bronze | 5% | من أول قطعة |
| فضي Silver | 10% | بعد 5,000 جنيه |
| ذهبي Gold | 15% | بعد 15,000 جنيه |

---

## 3. MODULE: invoice_deadline

### Module Info
```
Name: Invoice Deadline & Block
Technical name: invoice_deadline
Path: C:\odoo-modules\invoice_deadline
```

### File Structure
```
invoice_deadline/
├── __manifest__.py
├── __init__.py              ← imports: models, controllers
├── models/
│   ├── __init__.py          ← imports: res_partner, sale_order, account_move
│   ├── res_partner.py       ← adds is_blocked field
│   ├── sale_order.py        ← main logic + unified invoice + mark paid
│   └── account_move.py      ← auto-detect payment → unblock
├── controllers/
│   ├── __init__.py
│   └── main.py              ← website_sale overrides (block + merge redirect)
├── views/
│   ├── sale_order_views.xml ← form tab + status badge + list column
│   ├── res_partner_views.xml ← block banner + toggle
│   └── templates.xml        ← website cart/checkout alerts + countdown
├── static/src/js/
│   └── invoice_deadline.js  ← live countdown timer
└── data/
    └── cron.xml             ← daily cron job
```

---

## 4. INVOICE/ORDER LIFECYCLE — دورة حياة الفاتورة

```
اليوم 0: العميل يعمل Confirm من الكارت
           → SO يتفتح
           → invoice_open_date = اليوم
           → invoice_state = 'open'

اليوم 0-10: فترة مفتوحة
           → العميل يقدر يضيف منتجات على نفس الـ SO
           → لو عمل Confirm تاني → المنتجات تتضاف على SO الموجود (مش SO جديد)

اليوم 11: الـ Cron يشتغل
           → invoice_state: open → locked
           → تحذير يظهر للعميل

اليوم 11-16: فترة السماح (Grace Period)
           → العميل يقدر يفتح SO جديد (#2) بعداد منفصل
           → SO #1 لسه مقفول ينتظر الدفع

اليوم 17: الـ Cron يشتغل
           → لو SO #1 لسه مدفعش:
           → invoice_state: locked/grace → blocked
           → partner.is_blocked = True
           → كل SOs التانية للعميل بتتبلك كمان (cascade)

الدفع:
           → invoice_state = 'paid'
           → partner.is_blocked = False  ← (لسه مش متعمل - TODO)
```

---

## 5. DATABASE FIELDS — الحقول في الداتابيز

### على sale.order
| Field | Type | Description |
|-------|------|-------------|
| `invoice_open_date` | Datetime | تاريخ فتح الفاتورة (يوم الـ Confirm) |
| `invoice_deadline_date` | Datetime | تاريخ القفل (open_date + 10 أيام) — computed |
| `grace_end_date` | Datetime | تاريخ البلوك (open_date + 16 يوم) — computed |
| `invoice_state` | Selection | open / locked / grace / blocked / paid |
| `merged_into_so_id` | Many2one(sale.order) | الـ SO الموحَّد عليه (لو الـ SO الجديد اتدمج في موجود) |

### على res.partner
| Field | Type | Description |
|-------|------|-------------|
| `is_blocked` | Boolean | العميل محظور بسبب فواتير غير مدفوعة |

---

## 6. CURRENT CODE — الكود الحالي

> ملحوظة: الكود الحقيقي في الملفات. اللي هنا snapshot قديم — رجع للملفات نفسها للحقيقة الكاملة.

### models/res_partner.py
```python
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blocked = fields.Boolean(
        string='Blocked - Unpaid Invoices',
        default=False,
        copy=False,
    )
```

### models/sale_order.py
```python
from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    invoice_open_date = fields.Datetime(string='Invoice Open Date', readonly=True, copy=False)
    invoice_deadline_date = fields.Datetime(string='Invoice Deadline Date', compute='_compute_invoice_dates', store=True)
    grace_end_date = fields.Datetime(string='Grace End Date', compute='_compute_invoice_dates', store=True)
    invoice_state = fields.Selection(
        selection=[('open','Open'),('locked','Locked - Awaiting Payment'),
                   ('grace','Grace Period'),('blocked','Blocked'),('paid','Paid')],
        string='Invoice State', default='open', copy=False,
    )

    @api.depends('invoice_open_date')
    def _compute_invoice_dates(self):
        for order in self:
            if order.invoice_open_date:
                order.invoice_deadline_date = order.invoice_open_date + timedelta(days=10)
                order.grace_end_date = order.invoice_open_date + timedelta(days=16)
            else:
                order.invoice_deadline_date = False
                order.grace_end_date = False

    def _cron_update_invoice_states(self):
        # open → locked
        open_orders = self.search([
            ('invoice_state', '=', 'open'),
            ('invoice_deadline_date', '!=', False),
            ('invoice_deadline_date', '<=', fields.Datetime.now()),
        ])
        open_orders.write({'invoice_state': 'locked'})

        # locked/grace → blocked (cascade)
        escalate_orders = self.search([
            ('invoice_state', 'in', ('locked', 'grace')),
            ('grace_end_date', '!=', False),
            ('grace_end_date', '<=', fields.Datetime.now()),
        ])
        if escalate_orders:
            partners = escalate_orders.mapped('partner_id')
            escalate_orders.write({'invoice_state': 'blocked'})
            other_orders = self.search([
                ('partner_id', 'in', partners.ids),
                ('invoice_state', 'in', ('open', 'locked', 'grace')),
            ])
            other_orders.write({'invoice_state': 'blocked'})
            partners.write({'is_blocked': True})

    def action_confirm(self):
        # Block if customer is blocked
        for order in self:
            if order.partner_id.is_blocked:
                raise UserError(
                    "Your account is blocked due to unpaid invoices. "
                    "Please contact us to resolve."
                )
        res = super().action_confirm()
        # Set invoice_open_date only if no active SO exists for this partner
        for order in self:
            if not order.invoice_open_date:
                existing = self.search([
                    ('partner_id', '=', order.partner_id.id),
                    ('invoice_state', 'in', ('open', 'locked', 'grace')),
                    ('id', '!=', order.id),
                ], limit=1)
                if not existing:
                    order.invoice_open_date = fields.Datetime.now()
        return res
```

---

## 7. WHAT'S DONE ✅ — اللي اتعمل

```
✅ 1.  تعطيل auto_confirm module (Uninstalled)
✅ 2.  إنشاء invoice_deadline module
✅ 3.  الحقول على sale.order (invoice_open_date, deadline, grace, state)
✅ 4.  الحقل على res.partner (is_blocked)
✅ 5.  Cron Job يومي (open→locked→blocked + cascade)
✅ 6.  action_confirm يمنع البلوك
✅ 7.  تيست الـ Cron — شغال صح
✅ 8.  تيست منع الـ Confirm للعميل البلوك — شغال صح
✅ 9.  Unified Invoice — الـ SO الجديد بيتدمج في الموجود تلقائياً
✅ 10. Payment Closes Invoice — auto عبر account.move + manual button
✅ 11. Backend UI — تاب على SO form + badge + عمود في list + banner partner
✅ 12. Website UI — alerts + countdown + block checkout للمحظور
```

---

## 8. WHAT'S REMAINING ⏳ — اللي لسه هنعمله

### TODO: Remaining fixes + testing
```
✅ Red banner on blocked partner form
✅ Blocked toggle in Sales & Purchase tab
✅ Invoice Deadline tab on SO form (Timeline + Status + Mark as Paid)
✅ Invoice State badge in list view
✅ Mark as Paid button — changes state to paid, unblocks partner
✅ Unified Invoice — merge lines into existing SO, delete new SO, redirect to existing SO
✅ Website cart alert — shows info/warning/danger based on invoice_state
⏳ Website countdown timer — data-deadline arrives correctly ('2026-05-06 15:46:13')
   but JS not executing. Root cause: Odoo 17 loads assets_frontend bundle before DOM
   is ready, so DOMContentLoaded may not fire. Fix: convert JS to Odoo module format
   or use owl Component instead of plain DOMContentLoaded listener.
⏳ Payment auto-detection via account.move (needs testing with Create Invoice flow)
⏳ Website checkout block for blocked customers (needs blocked user test on website)
⏳ Clean up S00048 Cancelled record from old test
```

---

## 9. OPEN QUESTIONS — أسئلة مفتوحة

```
❓ لما البلوك يتفك بعد دفع SO #1:
   SO #2 اللي اتبلك قبل ما يخلص الـ 16 يوم بتاعته:
   → تكمل من اليوم اللي وقفت فيه؟
   → تبدأ من الصفر؟
   → تتلغي؟
   ← لازم نسأل صاحب العمل

❓ الـ unified invoice دلوقتي بيدمج فقط لو الـ SO الموجود في state ('sale','done').
   لو العميل عنده quotation (draft) — هل نضمها كمان؟
```

---

## 10. IMPORTANT NOTES — ملاحظات مهمة

```
1. الـ computed fields (invoice_deadline_date, grace_end_date) مش بتتحسب
   لو عدّلت invoice_open_date بـ SQL مباشرة.
   لازم تعمل UPDATE للحقلين يدوياً أو تستخدم Odoo shell.

2. الـ default=False على is_blocked مش بيشتغل على الـ records القديمة.
   لازم تعمل: UPDATE res_partner SET is_blocked = false WHERE is_blocked IS NULL;

3. اسم الداتابيز هو 'odoo' مش 'postgres'.

4. لما تعمل تغيير في الكود لازم:
   a. docker compose restart odoo
   b. Upgrade module من Apps أو عبر command line

5. الـ module اتعمله Missing license warning — عادي، مش error.
```

---

## 11. WORKFLOW FOR CLAUDE CODE — طريقة الشغل

لما تعمل أي تغيير:

```bash
# 1. عدّل الكود في C:\odoo-modules\invoice_deadline\

# 2. Upgrade
cd "C:\Users\Sherif Taha\Desktop"
docker compose exec odoo odoo -u invoice_deadline -d odoo --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# 3. Restart
docker compose restart odoo

# 4. تحقق من الـ logs لو في error
docker compose logs odoo --tail=30
```

---

*Last updated: 2026-04-26 — added Unified Invoice, Payment auto-close, Backend UI, Website UI*
*Developer: Sherif Taha*
*Project: BlueBee-Eg Odoo B2B E-commerce*
