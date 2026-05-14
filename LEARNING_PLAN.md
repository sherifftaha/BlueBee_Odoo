# خطة تعلم Module: invoice_deadline
## Learning Plan — BlueBee Odoo B2B Module

> **الهدف:** فهم كل ملف في الـ module — إيه اللي بيعمله وليه اتعمل كده.
> **الأسلوب:** من الأساسيات للتطبيق. كل مرحلة بتبني على اللي قبلها.
> **للاستخدام:** قول لـ Claude "اشرحلي المرحلة X" وهو يشرحها بالتفصيل.

---

## فهرس المراحل

| # | المرحلة | الملف / الموضوع | الأولوية |
|---|---------|----------------|---------|
| 1 | أساسيات Python | classes, inheritance, decorators | 🔴 لازم الأول |
| 2 | مفاهيم Odoo | ORM, Models, Fields, _inherit | 🔴 لازم الأول |
| 3 | بوابة الـ Module | `__manifest__.py` | 🟡 مهم |
| 4 | تحميل الكود | `__init__.py` (x2) | 🟡 مهم |
| 5 | إضافة حقل للعميل | `models/res_partner.py` | 🟢 سهل |
| 6 | المنطق الأساسي | `models/sale_order.py` | 🔴 الأهم |
| 7 | اكتشاف الدفع | `models/account_move.py` | 🟡 مهم |
| 8 | تعديل الموقع | `models/website.py` | 🟢 سهل |
| 9 | المهمة التلقائية | `data/cron.xml` | 🟡 مهم |
| 10 | إعدادات الدفع | `data/payment_config.xml` | 🟢 سهل |
| 11 | واجهة الـ Backend | `views/sale_order_views.xml` | 🟡 مهم |
| 12 | صفحة العميل | `views/res_partner_views.xml` | 🟢 سهل |
| 13 | واجهة الموقع | `views/templates.xml` | 🟡 مهم |
| 14 | سلوك الـ URLs | `controllers/main.py` | 🔴 مهم |
| 15 | العداد التنازلي | `static/src/js/invoice_deadline.js` | 🟢 سهل |
| 16 | نص زرار الكارت | `static/src/js/cart_modal_patch.js` | 🟢 سهل |

---

## المرحلة 1 — أساسيات Python

**قبل ما تفتح أي ملف في Odoo، لازم تعرف:**

| المفهوم | مثال من الكود الحقيقي | معناه |
|---------|----------------------|-------|
| `class` | `class SaleOrder(models.Model):` | تعريف نوع جديد |
| `inheritance` | `class SaleOrder(models.Model)` | SaleOrder بيورث من Model |
| `self` | `for order in self:` | يشير للـ records الحالية |
| `@decorator` | `@api.depends('invoice_open_date')` | يضيف سلوك على method |
| `for` loop | `for order in self:` | يلف على كل record |
| `timedelta` | `timedelta(days=10)` | يضيف/يطرح أيام من تاريخ |
| `raise` | `raise UserError(...)` | يوقف التنفيذ ويظهر error |

**سؤال اختبار:** إيه الفرق بين `class A:` و `class A(B):`؟

---

## المرحلة 2 — مفاهيم Odoo الأساسية

**المصطلحات الأساسية:**

```
Model  = جدول في الداتابيز         مثال: sale.order, res.partner
Field  = عمود في الجدول            مثال: invoice_state, is_blocked
Record = صف واحد في الجدول         مثال: طلب رقم S00042
_inherit = "ضيف على الموجود"        بدل ما تعيد الكتابة من الصفر
```

**أنواع الـ Fields الموجودة في الكود:**

| النوع | مثال | معناه |
|-------|------|-------|
| `fields.Boolean` | `is_blocked` | True / False |
| `fields.Datetime` | `invoice_open_date` | تاريخ + وقت |
| `fields.Selection` | `invoice_state` | قائمة اختيارات محددة |
| `fields.Many2one` | `merged_into_so_id` | علاقة بـ record في جدول تاني |

**الفرق المهم:**
```python
# حقل عادي — بيتحفظ في DB مباشرة
invoice_open_date = fields.Datetime()

# حقل محسوب — بيتحسب تلقائي لما invoice_open_date يتغير
invoice_deadline_date = fields.Datetime(compute='_compute_invoice_dates', store=True)
```

**سؤال اختبار:** لو عملت `store=False` على computed field، إيه اللي هيحصل؟

---

## المرحلة 3 — `__manifest__.py`

**الملف:** [`__manifest__.py`](__manifest__.py)

**وظيفته:** بطاقة هوية الـ module — Odoo بيقراه الأول عشان يعرف إيه اللي هيحمله.

**أهم الحاجات فيه:**

```python
'depends': ['sale', 'website_sale', 'account', ...]
# يعني: module تبعنا بيحتاج دول يكونوا مثبتين الأول

'data': ['data/cron.xml', 'views/sale_order_views.xml', ...]
# يعني: الملفات دي اتحملها في DB لما الـ module يتثبت

'assets': {'web.assets_frontend': ['static/src/js/...']}
# يعني: الـ JS دي اتضافها لكل صفحة على الموقع
```

**لو غلطت هنا:** الـ module مش هيتحمل خالص.

**سؤال اختبار:** لو حذفت `'account'` من الـ depends، إيه اللي هيحصل؟

---

## المرحلة 4 — ملفات `__init__.py`

**الملفات:**
- [`__init__.py`](__init__.py) — الرئيسي
- [`models/__init__.py`](models/__init__.py)
- [`controllers/__init__.py`](controllers/__init__.py)

**وظيفتهم:** بيقولوا لـ Python "حمّل الملفات دي".

```python
# __init__.py الرئيسي
from . import models      # حمّل فولدر models كله
from . import controllers # حمّل فولدر controllers كله

# models/__init__.py
from . import res_partner  # حمّل ملف res_partner.py
from . import sale_order   # حمّل ملف sale_order.py
from . import account_move
from . import website
```

**لو نسيت تضيف ملف هنا:** الكود اللي فيه مش هيشتغل — وأحياناً مفيش error واضح!

**سؤال اختبار:** لو ضفت ملف `models/loyalty.py` وما ضفتوش في `models/__init__.py`، هيحصل إيه؟

---

## المرحلة 5 — `models/res_partner.py`

**الملف:** [`models/res_partner.py`](models/res_partner.py)

**وظيفته:** يضيف حقل `is_blocked` على جدول العملاء.

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'   # "خد res.partner الموجود وضيف عليه"

    is_blocked = fields.Boolean(
        string='Blocked - Unpaid Invoices',
        default=False,   # العميل الجديد غير محظور بالـ default
        copy=False,      # لما تعمل duplicate للعميل، الحقل ده متنسخش
    )
```

**ليه الملف ده صغير؟**
لأن `res.partner` في Odoo الأصلي ضخم جداً (مئات الحقول والـ methods). إحنا مش بنعيد الكتابة — بنورث ونضيف بس.

**ليه `copy=False`؟**
عشان لما تعمل duplicate لعميل محظور، العميل الجديد يبدأ غير محظور.

**سؤال اختبار:** لو شيلت `copy=False`، إيه اللي هيحصل لو عملت duplicate لعميل محظور؟

---

## المرحلة 6 — `models/sale_order.py` ⭐

**الملف:** [`models/sale_order.py`](models/sale_order.py)

**وظيفته:** القلب كله — المنطق الأساسي للـ module.

### جزء 1: الحقول (السطور 10–43)

```python
invoice_open_date     # يوم الـ Confirm (اليوم صفر — بداية العداد)
invoice_deadline_date # يوم القفل = open_date + 10 أيام (computed)
grace_end_date        # يوم الحظر = open_date + 16 يوم (computed)
invoice_state         # open / locked / grace / blocked / paid
merged_into_so_id     # لو الطلب اندمج في طلب تاني، رابط للطلب الأصلي
```

### جزء 2: الـ Computed Fields (السطور 45–53)

```python
@api.depends('invoice_open_date')       # "احسبني لما invoice_open_date يتغير"
def _compute_invoice_dates(self):
    for order in self:
        if order.invoice_open_date:
            order.invoice_deadline_date = order.invoice_open_date + timedelta(days=10)
            order.grace_end_date        = order.invoice_open_date + timedelta(days=16)
```

**لماذا computed وليس يدوي؟** عشان الحسابات دايماً صح — مش محتاج تتذكر تحسبها في كل مكان.

### جزء 3: الـ Cron Method (السطور 55–80)

```python
def _cron_update_invoice_states(self):
    # بيشتغل كل يوم تلقائياً (بسبب cron.xml)

    # الخطوة 1: open → locked (لو فات 10 أيام)
    open_orders = self.search([('invoice_state', '=', 'open'),
                               ('invoice_deadline_date', '<=', now)])
    open_orders.write({'invoice_state': 'locked'})

    # الخطوة 2: locked → blocked (لو فات 16 يوم)
    # + يبلك العميل نفسه
    # + cascade: كل SOs التانية بتاعت العميل بتتبلك
```

### جزء 4: Override على `action_confirm` (السطور 82–136)

```python
def action_confirm(self):
    # الخطوة 1: لو العميل محظور → وقف وظهّر error
    # الخطوة 2: لو في SO مفتوح بالفعل → ادمج السطور فيه (Unified Invoice)
    # الخطوة 3: لأ مفيش → Confirm عادي وابدأ العداد
    res = super().action_confirm()  # ← نادي الـ method الأصلية في Odoo
    return res
```

**مفهوم Override:**
```
Odoo عنده action_confirm الأصلي.
إحنا بنعمل نفس الـ method في الـ class بتاعتنا.
Python هيشغّل النسخة بتاعتنا الأول.
super() = "دلوقتي شغّل الـ method الأصلية في Odoo".
```

### جزء 5: Helper Methods (السطور 138–199)

```python
action_mark_paid()       # Admin يسجل دفع يدوياً
action_unmark_paid()     # Admin يلغي التسجيل
_get_payment_info()      # يجيب رقم فودافون + البريد من System Parameters
_get_whatsapp_url()      # يبني رابط wa.me مع رسالة جاهزة فيها بيانات الفاتورة
```

**سؤال اختبار:** لو شيلت `super()` من `action_confirm`، إيه اللي هيحصل؟

---

## المرحلة 7 — `models/account_move.py`

**الملف:** [`models/account_move.py`](models/account_move.py)

**وظيفته:** لما فاتورة Odoo الرسمية تتدفع، يعمل sync تلقائي مع الـ Sale Orders.

```python
def write(self, vals):
    res = super().write(vals)             # الأول نفّذ الكتابة الأصلية
    if 'payment_state' in vals:           # لو في تغيير في حالة الدفع
        self._sync_sale_invoice_state()   # ابدأ المزامنة
    return res

def _sync_sale_invoice_state(self):
    # لكل فاتورة اتدفعت:
    # → ابحث عن الـ SOs المرتبطة بيها
    # → غيّر invoice_state بتاعتهم لـ 'paid'
    # → لو مفيش blocked orders تانية → ارفع الحظر عن العميل
```

**لماذا Override على `write` تحديداً؟**
لأن `write` بيمسك كل تغيير في أي حقل. لو Odoo أو أي module غيّر `payment_state` بأي طريقة، إحنا هنمسك التغيير ده.

**سؤال اختبار:** لو العميل دفع SO رقم 1 بس عنده SO رقم 2 لسه blocked، هل هيتفك الحظر؟

---

## المرحلة 8 — `models/website.py`

**الملف:** [`models/website.py`](models/website.py)

**وظيفته:** يغيّر نص الأزرار في صفحات الـ checkout.

```python
class Website(models.Model):
    _inherit = 'website'

    def _get_checkout_step_list(self):
        steps = super()._get_checkout_step_list()  # جيب الـ steps الأصلية
        for xmlids, vals in steps:
            if 'website_sale.cart' in xmlids:
                vals['main_button'] = _lt("Add to Invoice")  # غيّر النص
        return steps
```

**لماذا؟** في نظامنا مفيش دفع فوري. العميل بيضيف منتجات على فاتورة وبيدفع بعدين. فالنص "Proceed to Checkout" مش منطقي.

**سؤال اختبار:** لو شيلت الملف ده، الـ module هيشتغل؟ وإيه اللي هيختلف؟

---

## المرحلة 9 — `data/cron.xml`

**الملف:** [`data/cron.xml`](data/cron.xml)

**وظيفته:** يسجّل مهمة تلقائية تشتغل كل يوم.

```xml
<record id="ir_cron_update_invoice_states" model="ir.cron">
    <field name="name">Invoice Deadline: Update States</field>
    <field name="model_id" ref="sale.model_sale_order"/>
    <field name="code">model._cron_update_invoice_states()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>    <!-- كل يوم -->
    <field name="numbercall">-1</field>         <!-- للأبد -->
    <field name="active">True</field>
</record>
```

**لو ما كانش فيه cron.xml:**
الـ method `_cron_update_invoice_states` موجودة في الكود، بس مفيش حاجة تشغّلها تلقائياً.

**`noupdate="1"` معناها إيه؟**
لما تعمل upgrade للـ module، الـ record ده متتحدثش — بيتحفظ الإعداد اليدوي اللي عمله الـ admin.

**سؤال اختبار:** لو غيّرت `interval_type` من `days` لـ `hours`، إيه اللي هيحصل؟

---

## المرحلة 10 — `data/payment_config.xml`

**الملف:** [`data/payment_config.xml`](data/payment_config.xml)

**وظيفته:** يحفظ إعدادات الدفع في DB مش في الكود.

```xml
<record id="param_vodafone_cash" model="ir.config_parameter">
    <field name="key">invoice_deadline.vodafone_cash</field>
    <field name="value">01001234567</field>  <!-- القيمة الافتراضية -->
</record>
```

**لماذا في XML وليس في الكود مباشرة؟**
عشان صاحب الشغل يقدر يغيّر الأرقام من:
`Settings → Technical → System Parameters`
بدون ما يلمس الكود خالص.

**كيف الكود يقراها؟**
```python
# من sale_order.py
ICP = self.env['ir.config_parameter'].sudo()
vodafone = ICP.get_param('invoice_deadline.vodafone_cash', '')
```

**سؤال اختبار:** لو حذفت الملف ده، الـ module هيشتغل؟ وإيه اللي هيختلف؟

---

## المرحلة 11 — `views/sale_order_views.xml`

**الملف:** [`views/sale_order_views.xml`](views/sale_order_views.xml)

**وظيفته:** يضيف عناصر جديدة في صفحة الطلب بالـ Backend (Odoo Admin).

**اللي بيضيفه:**
1. تاب جديد "Invoice Deadline" فيه التواريخ والحالة وزرار Mark as Paid
2. Badge صغير في الـ status bar فوق الصفحة
3. عمود جديد في الـ List View

**المفهوم الأساسي: `inherit_id` + `xpath`**

```xml
<field name="inherit_id" ref="sale.view_order_form"/>
<!-- يعني: خد الـ view الأصلي ده وضيف عليه -->

<xpath expr="//page[@name='other_information']" position="after">
<!-- ابحث في XML عن page اسمه other_information، وحط كودي بعده -->
```

**المفهوم: `widget="badge"` + الألوان**

```xml
<field name="invoice_state"
       widget="badge"
       decoration-success="invoice_state in ('open', 'paid')"   <!-- أخضر -->
       decoration-warning="invoice_state in ('locked', 'grace')" <!-- أصفر -->
       decoration-danger="invoice_state == 'blocked'"/>           <!-- أحمر -->
```

**سؤال اختبار:** لو عايز تضيف عمود جديد في الـ List View، فين بتضيفه؟

---

## المرحلة 12 — `views/res_partner_views.xml`

**الملف:** [`views/res_partner_views.xml`](views/res_partner_views.xml)

**وظيفته:** يضيف على صفحة العميل في الـ Backend.
- Banner أحمر في الأعلى لو العميل محظور
- Toggle (زرار on/off) في تاب Sales & Purchase

**المفهوم: `invisible`**

```xml
<div class="alert alert-danger" invisible="not is_blocked">
    <!-- هيتعرض بس لو is_blocked = True -->
```

ده مش بيخفي الحقل من DB — بيخفيه من الشاشة بس.

**سؤال اختبار:** لو غيّرت `invisible="not is_blocked"` لـ `invisible="1"`، إيه اللي هيحصل؟

---

## المرحلة 13 — `views/templates.xml`

**الملف:** [`views/templates.xml`](views/templates.xml) — 359 سطر

**وظيفته:** كل اللي العميل بيشوفه على الموقع.

**فيه 4 أجزاء:**

| الجزء | الـ template id | الوظيفة |
|-------|----------------|---------|
| 1 | `blocked_account_page` | صفحة "/shop/blocked" |
| 2 | `portal_my_orders_invoice_state` | 3 أعمدة جديدة في صفحة "فواتيري" |
| 3 | `header_invoices_link` | زرار "My Invoices" في الـ Navbar |
| 4 | `portal_sale_order_pay_section` | Card على صفحة الطلب: حالة + دفع + واتساب |

**المفهوم: Qweb Templating**

```xml
<t t-if="order.invoice_state == 'open'">
    <span class="badge text-bg-info">مفتوحة — Open</span>
</t>
<t t-elif="order.invoice_state == 'blocked'">
    <span class="badge text-bg-danger">محظورة — Blocked</span>
</t>
```

ده الـ Odoo templating language — زي if/else في Python بس في HTML.

**مفهوم `t-att-data-deadline`:**
```xml
<span class="bb_countdown" t-att-data-deadline="order.invoice_deadline_date">
```
يعني: "حط قيمة `invoice_deadline_date` في الـ attribute `data-deadline` في الـ HTML".
الـ JavaScript بيقراها بعدين ويعمل العداد.

**سؤال اختبار:** إزاي بيوصل التاريخ من الـ Python للـ JavaScript؟

---

## المرحلة 14 — `controllers/main.py`

**الملف:** [`controllers/main.py`](controllers/main.py)

**وظيفته:** بيتحكم في سلوك الموقع لما العميل يفتح URLs معينة.

**فيه 3 classes:**

### Class 1: `WebsiteSaleInvoiceDeadline`
```python
# بيورث من الـ controller الأصلي في Odoo
class WebsiteSaleInvoiceDeadline(WebsiteSale):

    @http.route()  # بيعمل override على route موجود
    def shop(self, ...):
        if self._bb_is_blocked():
            return request.redirect('/shop/blocked')  # محظور → ارفضه
        return super().shop(...)  # مش محظور → Odoo الأصلي

    def confirm_order(self, **post):
        # السلوك الجديد:
        # لو في SO مفتوح → ادمج الكارت فيه → روح /my/orders/ID
        # لأ → Confirm جديد → روح /my/orders/ID
        # في الحالتين: مفيش صفحة دفع فورية
```

### Class 2: `BlockedAccountController`
```python
@http.route('/shop/blocked', auth='public', website=True)
def blocked_page(self, **kw):
    return request.render('invoice_deadline.blocked_account_page')
```
يعني: لما حد يفتح `/shop/blocked` → اعرضله الصفحة الحمراء.

### Class 3: `CloseInvoiceController`
```python
@http.route('/my/orders/<int:order_id>/close_for_payment',
            methods=['POST'], auth='user')
def close_for_payment(self, order_id, **kw):
    # لما العميل يضغط "دفع وتقفيل"
    order.invoice_state = 'locked'
```

**مفهوم `sudo()`:**
```python
order_sudo = order.sudo()
```
يعني: "نفّذ العملية دي بصلاحيات admin". لازم لأن العميل على الموقع مش عنده صلاحية تعديل Sale Orders مباشرة.

**مفهوم `csrf_token`:**
```python
<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
```
حماية من هجمات CSRF — Odoo بيرفض أي POST request من غير التوكن ده.

**سؤال اختبار:** لو حذفت `if self._bb_is_blocked(): return redirect(...)` من shop، إيه اللي هيحصل؟

---

## المرحلة 15 — `static/src/js/invoice_deadline.js`

**الملف:** [`static/src/js/invoice_deadline.js`](static/src/js/invoice_deadline.js)

**وظيفته:** عداد تنازلي في المتصفح يعرض "كام يوم وساعة فاضل".

```javascript
// 1. إزاي يقرأ التاريخ من HTML
// data-deadline="2026-05-06 15:46:13" ← جاي من templates.xml
const deadline = new Date(el.dataset.deadline.replace(' ', 'T') + 'Z');

// 2. إزاي يحسب الوقت الفاضل
const diffMs = deadline - new Date();  // الفرق بالميلي ثانية
const days   = Math.floor(diffMs / 86400000);

// 3. إزاي يعمل تحديث كل دقيقة
setInterval(tick, 60000);
```

**الرابط بين Python → HTML → JavaScript:**
```
Python:     order.invoice_deadline_date = datetime(2026, 5, 6, 15, 46)
                          ↓ templates.xml
HTML:       <span data-deadline="2026-05-06 15:46:13">
                          ↓ invoice_deadline.js
Browser:    "3d 4h" ← يتحدث كل دقيقة
```

**`/** @odoo-module **/` في السطر الأول معناها إيه؟**
بتقول لـ Odoo "الملف ده ES6 module" — لازم يكون موجود عشان الـ JS يشتغل صح في Odoo 17.

**سؤال اختبار:** ليه بنضيف `+ 'Z'` على التاريخ؟

---

## المرحلة 16 — `static/src/js/cart_modal_patch.js`

**الملف:** [`static/src/js/cart_modal_patch.js`](static/src/js/cart_modal_patch.js)

**وظيفته:** يغيّر النص في الـ modal اللي بيظهر لما تضيف منتج للكارت.

```javascript
publicWidget.registry.WebsiteSale.include({
    _onProductReady: function () {
        this.optionalProductsModal = new OptionalProductsModal(this.$form, {
            okButtonText: _t('Add to Invoice'),  // ← النص الجديد
            cancelButtonText: _t('Continue Shopping'),
        }).open();
    },
});
```

**مفهوم `.include()`:**
```
ده JavaScript inheritance في Odoo — نفس مفهوم _inherit في Python.
WebsiteSale.include({...}) = "خد الـ Widget الأصلي وضيف/عدّل عليه"
```

**سؤال اختبار:** لو شيلت الملف ده، الـ module هيشتغل؟ وإيه اللي هيختلف؟

---

## ملخص الخطة الزمنية

```
الأسبوع 1:  المراحل 1-2  ← Python أساسيات + Odoo ORM
الأسبوع 2:  المراحل 3-5  ← __manifest__ + __init__ + res_partner
الأسبوع 3:  المراحل 6-7  ← sale_order (الأهم) + account_move
الأسبوع 4:  المراحل 8-10 ← website + cron + payment_config
الأسبوع 5:  المراحل 11-13 ← Views كلها (backend + frontend)
الأسبوع 6:  المراحل 14-16 ← Controllers + JavaScript
```

---

## الـ "لو حذفت الملف ده" اختبار

> **أهم سؤال تسأله على أي ملف:** لو حذفت الملف ده، إيه اللي هيتكسر؟

| الملف المحذوف | النتيجة |
|--------------|---------|
| `res_partner.py` | مفيش `is_blocked` → الـ cron هيـcrash |
| `sale_order.py` | مفيش منطق للمواعيد والحظر |
| `account_move.py` | الدفع من Odoo مش بيغيّر invoice_state تلقائياً |
| `cron.xml` | الحالات مش بتتغير تلقائياً — لازم تعمل كل حاجة يدوي |
| `controllers/main.py` | العميل المحظور يقدر يتسوق — مش في redirect |
| `templates.xml` | الموقع مفيهوش أي معلومات عن الفواتير |
| `sale_order_views.xml` | الـ Backend مفيهوش تاب Invoice Deadline |
| `invoice_deadline.js` | العداد التنازلي مش بيشتغل — بيفضل "..." |

---

## للاستخدام مع Claude

```
"اشرحلي المرحلة 6 جزء 4 — Override على action_confirm"
"اشرحلي المفهوم: sudo() في Odoo"
"اشرحلي إيه الفرق بين computed store=True و store=False"
"اشرحلي إزاي بيوصل التاريخ من Python للـ JavaScript"
"اسألني أسئلة على المرحلة 9 عشان أتأكد إني فهمت"
```

---

*Last updated: 2026-04-27*
*Module: invoice_deadline — BlueBee-Eg*
