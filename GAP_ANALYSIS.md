# GAP ANALYSIS — BlueBee Invoice Deadline Module
## مقارنة الكود الحالي بـ BUSINESS_LOGIC.md

**تاريخ التحليل | Analysis Date:** 2026-05-16  
**مرجع Business Logic:** `BUSINESS_LOGIC.md` v2026-05-16  
**الكود المحلَّل:** `invoice_deadline` module — الملفات الفعلية في الريبو  

---

## 📊 ملخص سريع | Quick Summary

| الفئة Category | العدد Count |
|---|---|
| ✅ موجود ومطابق — Implemented & Correct | 13 |
| ❌ ناقص تماماً — Missing Entirely | 7 |
| ⚠️ موجود ومحتاج تعديل — Exists but Needs Fix | 5 |

---

## ✅ القسم 1: موجود ومطابق للـ Business Logic

### 1.1 حالات الفاتورة الخمسة — 5 Invoice States
**BL Reference:** Section 1  
الـ `invoice_state` selection field فيه الـ 5 قيم المطلوبة: `open`, `locked`, `grace`, `blocked`, `paid`. الـ transitions في الـ cron صح جزئياً (تفاصيل في القسم 3).

### 1.2 الحقول الزمنية — Deadline Fields
**BL Reference:** Section 1  
`invoice_open_date`, `invoice_deadline_date` (open + 10 days), `grace_end_date` (open + 16 days) — موجودة ومحسوبة صح.

### 1.3 الحد الأدنى والرسوم — Minimum & Surcharge
**BL Reference:** Section 4  
`MIN_PIECES = 6`, `FEE_PER_PIECE = 25 EGP`. الرسوم بتتضاف كـ line item في الفاتورة مع وصف ثنائي اللغة. الحساب صح (عدد القطع × 25).

### 1.4 الـ Cron: open → locked (يوم 10)
**BL Reference:** Section 1  
الـ cron اليومي بيحوّل `open` → `locked` بعد 10 أيام. شغال صح.

### 1.5 الـ Cron: locked/grace → blocked (يوم 16) + Cascade
**BL Reference:** Section 6  
لما التاجر يتجاوز يوم 16، كل فواتيره بتتبلك وكمان `is_blocked = True` على الـ partner. الـ cascade lock شغال صح.

### 1.6 منع الـ Confirm للمحظور — Block Enforcement
**BL Reference:** Section 6  
`action_confirm` بترفض لو `partner.is_blocked = True` برسالة واضحة. شغال صح.

### 1.7 الـ Unified Invoice — Cart Merging
**BL Reference:** Section 5, Priority #2  
لما التاجر يضيف منتجات وعنده فاتورة `open` قايمة، الـ lines بتتضاف عليها بدل إنشاء فاتورة جديدة. شغال صح.

### 1.8 Mark as Paid + Unblock
**BL Reference:** Section 2  
`action_mark_paid` بيحوّل `invoice_state = 'paid'` وبيفك الحظر عن الـ partner لو مفيش فواتير متأخرة تانية متبقية. `action_unmark_paid` موجود كمان.

### 1.9 Auto-Payment Detection عبر account.move
**BL Reference:** Section 2  
لما الإدارة تسجل دفعة في Odoo مالي (`payment_state = paid/in_payment`)، الـ SO بيتحوّل لـ `paid` تلقائياً وبيفك الحظر.

### 1.10 قفل يدوي من التاجر — Customer-Initiated Lock
**BL Reference:** Section 2  
Route `/my/orders/<id>/close_for_payment` بيسمح للتاجر يقفل فاتورته يدوياً قبل ما الـ cron يقفلها (من `open` → `locked`).

### 1.11 Website Blocking
**BL Reference:** Section 6  
الـ shop/cart/checkout routes بتحجب المحظورين وبتودّيهم لصفحة `/shop/blocked` فيها رسالة الحظر + زر واتس للدعم. شغال صح.

### 1.12 Backend Admin UI
**BL Reference:** (implied throughout)  
تاب "Invoice Deadline" على SO form + badge للحالة + عمود في list + banner على partner form. كلها موجودة.

### 1.13 Portal UI — الصفحة الأمامية للتاجر
**BL Reference:** Sections 1, 2, 7  
صفحة الفاتورة بتعرض: حالة الفاتورة، العداد، معلومات الدفع (فودافون كاش، بريد)، زر "Pay & Close"، زر واتس لإرسال إثبات الدفع.

---

## ❌ القسم 2: ناقص ومحتاج يتضاف

### 2.1 ❌ نوعين الدفع: شحن vs استكمال — Two Payment Types (BIGGEST GAP)
**BL Reference:** Section 3 (الكل — 100% مش موجود)

مفيش أي أثر للـ Continuation mode في الكود. ده يشمل:

- **لا يوجد** field للـ payment type على الـ SO (`payment_type = 'shipping' | 'continuation'`)
- **لا يوجد** UI لاختيار الشحن أو الاستكمال وقت طلب الدفع
- **لا يوجد** منطق الاستكمال:
  - العداد الجديد (10 أيام تبدأ من الأول) عند دخول وضع الاستكمال
  - الفاتورة تفضل مفتوحة للإضافة بعد تأكيد دفع الاستكمال
  - الحد الأقصى 20 قطعة + auto-lock عند الوصول لـ 20
  - إشعار "وصلت للحد الأقصى، الفاتورة هتتشحن"
  - منع تحويل شحن → استكمال (الشحن قرار نهائي)
- **لا يوجد** تأكيد العنوان وطريقة التواصل وقت اختيار الشحن
- **لا يوجد** رسالة "لا يوجد إلغاء ذاتي — تواصل مع خدمة العملاء" لفواتير الاستكمال

### 2.2 ❌ رفع إثبات الدفع — Payment Proof Upload
**BL Reference:** Section 2, steps 5-6

ملاحظة في الواجهة إن التاجر "يرسل إثبات الدفع عبر واتس" — لكن مفيش:
- Upload للـ screenshot داخل الموقع نفسه
- ملاحظة اختيارية من التاجر تترفع مع إثبات الدفع
- Flag `has_pending_payment` على الـ SO المقفولة بيشير إن في دفعة في الانتظار

الواتس بيعمل بديل عملي مؤقت، لكن البيزنس لوجيك بيطلب رفع داخل الموقع.

### 2.3 ❌ Workflow تأكيد/رفض الإدارة — Admin Confirm/Reject Workflow
**BL Reference:** Section 2 (Admin confirmation subsection)

دلوقتي الإدارة بتستخدم "Mark as Paid" زر بس. مفيش:
- زر "تأكيد الدفع" منفصل عن "رفض الدفع"
- خانة كتابة "سبب الرفض" عند الرفض
- Queue لإثباتات الدفع المنتظرة المراجعة من الإدارة
- الـ SO بيفضل `locked` بعد الرفض (ده ممكن يكون صح في السلوك الحالي، لكن مش متحكم به explicitly)

### 2.4 ❌ إشعارات الرفض — Rejection Notifications
**BL Reference:** Section 7

لما الإدارة ترفض الدفع:
- مفيش حقل `rejection_reason` على الـ SO
- مفيش عرض سبب الرفض على صفحة الفاتورة (دائم لحد ما يدفع تاني)
- مفيش in-app notification مؤقت أعلى الصفحة
- مفيش `Chatter` message للتاجر بسبب الرفض

### 2.5 ❌ غرامة الـ 1000 جنيه — 1000 EGP Penalty
**BL Reference:** Section 6 (Penalty subsection)

لما التاجر يتبلك:
- مفيش منطق لإضافة غرامة 1000 جنيه للفاتورة الأصلية
- مفيش Product/line-item للغرامة
- مفيش UI للإدارة يوضحلها إن المطلوب = الفاتورة + الغرامة
- الـ `action_mark_paid` مش بتتحقق من دفع الغرامة قبل فك الحظر

### 2.6 ❌ الـ `grace` State Transition
**BL Reference:** Section 1 (grace row)

الـ `grace` state موجود في الـ selection field ومستخدم في بعض الشروط، لكن **لا يوجد كود يحوّل أي فاتورة لـ `grace` state**.

- الـ cron بيروح من `open` → `locked` (يوم 11)، لكن مفيش `locked` → `grace`
- الـ cron الثاني بيروح من `locked | grace` → `blocked` (يوم 16)

النتيجة: التاجر بيفضل في `locked` طول الوقت لحد ما يتبلك. البيزنس لوجيك بيقول إن `grace` = يوم 11-16 لازم يكون distinct state.

### 2.7 ❌ Unified Invoice Priority #1 (Continuation)
**BL Reference:** Section 5, Priority #1

الكود بيدعم فقط Priority #2 (merge في `open` invoice). Priority #1 يقول:
> لو في فاتورة continuation مدفوعة جزئياً + مفتوحة للإضافة → اضف عليها (أولوية أعلى من الـ open invoice)

ده ما ينفعش يتعمل غير بعد ما Section 3 (Continuation mode) يتنفذ.

---

## ⚠️ القسم 3: موجود ومحتاج تعديل

### 3.1 ⚠️ توقيت الرسوم — Surcharge Timing
**BL Reference:** Section 3 & Section 4

**المشكلة:**  
الرسوم دلوقتي بتتحسب لايف على أي SO في حالة `open` وبتظهر دايماً كـ line item. لكن البيزنس لوجيك بيقول:
> الرسوم تتطبق **وقت الشحن الفعلي**، مش وقت الاستكمال.

**مثال BL:**  
تاجر عنده 4 قطع دفع استكمال → مفيش رسوم. لما قرر يشحن → 4 × 25 = 100 جنيه رسوم.

**التعديل المطلوب:**  
- في وضع الاستكمال (بعد تنفيذ Section 3): الرسوم تتحجب أو تتصفر
- الرسوم تتضاف وتظهر فقط عند اختيار "شحن" وقت طلب الدفع
- لو بقى فوق 6 في الاستكمال → الرسوم تتشال حتى لو كانت اتضافت

### 3.2 ⚠️ إيقاف/استئناف عداد فاتورة #2 بعد البلوك — Pause/Resume Timer
**BL Reference:** Section 6 (Invoice #2 after unblock)

**المطلوب:**  
بعد فك البلوك، فاتورة #2 تكمل من اليوم اللي وقفت فيه (مش تبدأ من الأول، ومش تحسب الأيام اللي كانت blocked).

**المشكلة في الكود:**  
- مفيش field `paused_at` على الـ SO
- لما البلوك يتفك في `action_mark_paid`، الـ siblings بتترجع لحالتها (`open`/`locked`/`grace`) بناءً على الـ dates الأصلية
- الـ `invoice_deadline_date` و `grace_end_date` محسوبان على `invoice_open_date + 10/16 days` ثابت
- النتيجة: لو فاتورة #2 كان فاضل ليها 7 أيام لما اتبلكت، بعد فك البلوك الأيام المحسوبة هتكون أقل لأن الوقت استمر في الحساب خلال فترة البلوك

**التعديل المطلوب:**  
- إضافة field `paused_at` (Datetime)
- وقت البلوك: تخزين `paused_at = now()`
- وقت فك البلوك: حساب `pause_duration = now() - paused_at` وتمديد `invoice_open_date` بنفس المدة

### 3.3 ⚠️ Confirmation Modal للرسوم عند طلب الدفع
**BL Reference:** Section 2, step 2

**المطلوب من BL:**  
> لو القطع أقل من 6 وقت الشحن، يظهر **Confirmation Modal** فيه:
> - تنبيه برسوم +25ج/قطعة
> - الإجمالي بالرسوم
> - خياران: "أكمل التسوق" / "أكد الدفع بالرسوم"

**الموجود حالياً:**  
- تحذير ثابت في أعلى صفحة الفاتورة (not a modal)
- `cart_modal_patch.js` بيعدّل على أزرار الـ optional products modal — مش نفس الـ modal المطلوب

**التعديل المطلوب:**  
Modal يظهر لما التاجر يضغط "Pay & Close" ولو القطع أقل من 6، بيعرض الرسوم المحسوبة وخيار "أكمل التسوق" vs "أكد الدفع".

### 3.4 ⚠️ البحث في action_confirm عن فاتورة موجودة
**BL Reference:** Section 5

**المشكلة:**  
في `sale_order.py`، `action_confirm` بيبحث عن:
```python
('invoice_state', 'in', ('open', 'locked', 'grace'))
```
لتحديد إذا `invoice_open_date` يتضبط. لكن حسب الـ BL، المنتجات لازم تتضاف **فقط** على فاتورة `open` (مش `locked` أو `grace`). الفواتير المقفولة مش المفروض تقبل merge.

> ملحوظة: الـ merge الفعلي بيتم في الـ controller وبيبحث عن `open` فقط — المشكلة في `action_confirm` اللي بيخلي `invoice_open_date` ما يتضبطش حتى لو الفاتورة الموجودة `locked`.

**التعديل المطلوب:**  
في `action_confirm`، الشرط لازم يكون `('invoice_state', '=', 'open')` بس، مش `('in', ('open','locked','grace'))`.

### 3.5 ⚠️ الـ JS Countdown Timer
**BL Reference:** (implied — portal UI)

**المشكلة** (موثقة في CLAUDE.md):  
البيانات `data-deadline` بتوصل صح، لكن الـ JS مش بيشتغل أحياناً بسبب:
> Odoo 17 loads assets_frontend bundle before DOM is ready, so DOMContentLoaded may not fire.

**التعديل المطلوب:**  
تحويل الـ `invoice_deadline.js` لـ Odoo module format أو استخدام `owl` component بدل `DOMContentLoaded`.

---

## 📋 القسم 4: ترتيب الـ Implementation المقترح

الترتيب مبني على الـ dependencies — كل item بيعتمد على اللي قبله.

### المرحلة 1 — Bug Fixes (لا dependencies)
*كل واحدة مستقلة، يمكن تتعمل بالتوازي*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 1.1 | إصلاح الـ JS Countdown (Odoo module format) | `static/src/js/invoice_deadline.js` | 3.5 |
| 1.2 | تصحيح شرط البحث في `action_confirm` | `models/sale_order.py` | 3.4 |
| 1.3 | إضافة `paused_at` field + pause/resume logic | `models/sale_order.py` | 3.2 |

### المرحلة 2 — Grace State (يعتمد على: لا شيء)
*يمكن تتعمل بعد Phase 1 أو بالتوازي*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 2.1 | إضافة `locked` → `grace` transition في الـ cron | `models/sale_order.py` | 2.6 |
| 2.2 | تحديد trigger الـ grace: هل هو وقت المحاولة اليدوية اللي مش متوفر؟ أم يوم 11 مباشرة؟ | قرار من نانسي | 2.6 |

### المرحلة 3 — 1000 EGP Penalty (يعتمد على: Phase 1)
*يتعمل بعد Phase 1 لأنه بيعتمد على Mark as Paid flow*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 3.1 | إنشاء product للغرامة (`product_penalty_1000`) | `data/` XML جديد | 2.5 |
| 3.2 | إضافة penalty line تلقائياً لما SO يتبلك | `models/sale_order.py` في `_cron_update_invoice_states` | 2.5 |
| 3.3 | `action_mark_paid` تتحقق من الغرامة مدفوعة قبل فك الحظر | `models/sale_order.py` | 2.5 |
| 3.4 | Backend UI: إظهار total مع الغرامة على form الإدارة | `views/sale_order_views.xml` | 2.5 |

### المرحلة 4 — Payment Proof + Admin Workflow (يعتمد على: Phase 1)
*مستقلة عن الـ Continuation، لكن مهمة للـ Phase 1 الكاملة*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 4.1 | إضافة `has_pending_payment` flag على SO | `models/sale_order.py` | 2.2 |
| 4.2 | Upload screenshot في portal (Odoo attachment) | `controllers/main.py` + `views/templates.xml` | 2.2 |
| 4.3 | خانة ملاحظة التاجر اختيارية | `models/sale_order.py` + portal template | 2.2 |
| 4.4 | Backend: قائمة "فواتير تنتظر التأكيد" | `views/sale_order_views.xml` (list filter) | 2.3 |
| 4.5 | زر "تأكيد الدفع" + زر "رفض الدفع" (بخانة سبب) في backend | `models/sale_order.py` + views | 2.3 |
| 4.6 | حقل `rejection_reason` على SO | `models/sale_order.py` | 2.4 |
| 4.7 | عرض سبب الرفض على portal page للتاجر | `views/templates.xml` | 2.4 |
| 4.8 | In-app notification مؤقت عند الرفض | `views/templates.xml` أو JS | 2.4 |

### المرحلة 5 — Confirmation Modal للرسوم (يعتمد على: Phase 4)
*بتبقى أوضح لما يكون في workflow دفع واضح*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 5.1 | Modal HTML في portal template | `views/templates.xml` | 3.3 |
| 5.2 | JS logic للـ modal (show on "Pay & Close" if < 6 pieces) | `static/src/js/` | 3.3 |

### المرحلة 6 — Continuation Mode (يعتمد على: الكل)
*أكبر feature — تحتاج كل الـ phases السابقة مكتملة ومستقرة*

| # | الـ Task | الملف/المكان | الـ Gap Ref |
|---|---|---|---|
| 6.1 | إضافة `payment_type` field (`shipping`/`continuation`) على SO | `models/sale_order.py` | 2.1 |
| 6.2 | UI اختيار الشحن أو الاستكمال في صفحة الدفع | `views/templates.xml` + controller | 2.1 |
| 6.3 | منطق الاستكمال: عداد جديد 10 أيام، فاتورة تفضل open | `models/sale_order.py` | 2.1 |
| 6.4 | Max 20 pieces: auto-lock + notification | `models/sale_order.py` + templates | 2.1 |
| 6.5 | تحويل continuation → shipping (بدون العكس) | `models/sale_order.py` + portal | 2.1 |
| 6.6 | تعديل surcharge timing: تظهر فقط عند shipping | `models/sale_order.py` | 3.1 |
| 6.7 | Unified Invoice Priority #1 (continuation أولوية) | `controllers/main.py` | 2.7 |
| 6.8 | رسالة "تواصل مع خدمة العملاء" لإلغاء فاتورة الاستكمال | `views/templates.xml` | 2.1 |

---

## 🔑 القرارات المطلوبة قبل Phase 2 (Grace State)

قبل ما نبدأ Phase 2، محتاجين توضيح لسؤال واحد:

**سؤال:** الـ `grace` state — متى بالضبط بتتحوّل إليه الفاتورة؟

**الخيار أ:** الـ cron يوم 11 يحوّل مباشرة `open` → `grace` (بدل `locked`). يعني grace هو المرحلة الوحيدة بعد اليوم 10.  
**الخيار ب:** الـ cron يوم 11 يحوّل `open` → `locked`، وبعدين transition إضافي من `locked` → `grace`... لكن متى؟  
**الخيار ج:** الـ `locked` والـ `grace` بيوصفوا نفس الحالة من وجهتين مختلفتين — locked (من جهة التاجر) وgrace (من جهة الـ system) — وهما نفس الـ state.

> **ملحوظة:** الـ BL document في قسم 1 بيقول `grace` "من `locked` بعد 10 أيام" — لكن ده ممكن يكون تايبو والمعنى هو "من `open` بعد 10 أيام". محتاج توضيح.

---

## 📝 سجل التحليل | Analysis Log

| التاريخ | التفصيل |
|---|---|
| 2026-05-16 | تحليل أولي شامل — مقارنة BUSINESS_LOGIC.md بالكود الفعلي في الريبو |

---

**End of GAP_ANALYSIS.md**
