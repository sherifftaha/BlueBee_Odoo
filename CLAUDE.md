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
- حد أدنى 6 قطع للشحن، أقل من 6 بزيادة 25 جنيه للقطعة
- الرسوم تتطبق **وقت الشحن الفعلي فقط** — مش وقت الاستكمال
- نظام الولاء (Loyalty) **مؤجل لـ Phase 2** — محتاج بيانات حقيقية قبل التصميم

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
│   ├── __init__.py          ← imports: res_partner, sale_order, account_move, website
│   ├── res_partner.py       ← adds is_blocked field
│   ├── sale_order.py        ← main logic + unified invoice + payment workflow
│   ├── account_move.py      ← auto-detect payment → mark paid
│   └── website.py           ← renames "Add to Cart" → "Add to Invoice"
├── controllers/
│   ├── __init__.py
│   └── main.py              ← website_sale overrides (block + merge + close_for_payment)
├── views/
│   ├── sale_order_views.xml  ← form tab + status badge + list column + admin buttons
│   ├── res_partner_views.xml ← block banner + toggle
│   └── templates.xml         ← portal pages + countdown + payment section
├── static/src/js/
│   ├── invoice_deadline.js   ← live countdown timer
│   └── cart_modal_patch.js   ← patches "Add to Cart" label in optional products modal
└── data/
    ├── cron.xml                    ← daily cron job
    ├── payment_config.xml          ← Vodafone Cash / postal / WhatsApp system params
    └── below_minimum_fee_product.xml ← service product for 25 EGP/piece surcharge
```

---

## 4. INVOICE/ORDER LIFECYCLE — دورة حياة الفاتورة

### 4.1 الحالات الست — 6 Invoice States

| الحالة State | المعنى | Trigger |
|---|---|---|
| `open` 🟦 | الفاتورة مفتوحة، التاجر يضيف بحرية، العداد شغال (10 أيام) | إنشاء الفاتورة أو دخول وضع الاستكمال |
| `locked` 🟧 | مقفولة للإضافة، في انتظار دفع | (أ) Cron بعد 10 أيام، (ب) التاجر طلب دفع يدوياً |
| `grace` 🟨 | يوم 11-16، التاجر يقدر يفتح فاتورة #2 بعداد منفصل | Cron: `locked` → `grace` يوم 11 |
| `blocked` 🟥 | يوم 17، محظور تماماً، cascade على كل الفواتير | Cron: `locked`/`grace` → `blocked` يوم 17 |
| `paid` ✅ | الدفع اتأكد، الفاتورة أُغلقت نهائياً وخرجت للشحن | الإدارة تأكد دفعة شحن |
| `continuation` 🔁 | دفع جزئي اتأكد، الفاتورة مفتوحة للإضافة لحد 20 قطعة | الإدارة تأكد دفعة استكمال |

> **ملحوظة:** `continuation` مش موجود في الكود بعد — مطلوب تنفيذه في Phase 2 من الـ GAP_ANALYSIS.md

### 4.2 السيناريو الكامل — Full Lifecycle

```
اليوم 0: التاجر يعمل Confirm من الكارت
           → SO يتفتح
           → invoice_open_date = اليوم
           → invoice_state = 'open'

اليوم 0-10: فترة مفتوحة (open)
           → التاجر يضيف منتجات على نفس الـ SO (Unified Invoice)
           → لو Confirm تاني → المنتجات تتضاف على SO الموجود (مش SO جديد)
           → التاجر يقدر يطلب دفع يدوياً → اختيار: شحن أو استكمال

اليوم 11: الـ Cron يشتغل
           → invoice_state: open → grace
           → تحذير يظهر للعميل

اليوم 11-16: فترة السماح (grace)
           → التاجر يقدر يفتح SO جديد (#2) بعداد منفصل
           → SO #1 لسه مقفول ينتظر الدفع

اليوم 17: الـ Cron يشتغل
           → لو SO #1 لسه مدفعش:
           → invoice_state: locked/grace → blocked
           → partner.is_blocked = True
           → كل SOs التانية للعميل بتتبلك كمان (cascade)

الدفع (شحن):
           → invoice_state = 'paid'
           → الفاتورة تخرج للشحن
           → partner.is_blocked = False (لو كان بلوك)

الدفع (استكمال):
           → invoice_state = 'continuation'
           → عداد جديد 10 أيام يبدأ من الأول
           → الفاتورة تفضل مفتوحة للإضافة لحد 20 قطعة إجمالي
           → عند وصول 20 قطعة → auto-lock + إشعار "الفاتورة هتتشحن"
           → التاجر يقدر يحول continuation → shipping في أي وقت
           → الشحن قرار نهائي (مش بيرجع استكمال)
```

### 4.3 سيناريو البلوك والفك — Block & Unblock

```
يوم 17 بدون دفع:
   → كل فواتير التاجر → blocked
   → partner.is_blocked = True
   → التاجر يشوف رسالة الحظر في كل صفحة + زر واتس
   → المطلوب للفك: الفاتورة الأصلية + غرامة 1000 جنيه
   → الإدارة بتشيل الحظر يدوياً بعد تأكيد الدفع

فك البلوك:
   → SO #1 → paid
   → SO #2 اللي اتبلك → تكمل من اليوم اللي وقفت فيه (مش من الأول)
   → Technical: paused_at timestamp محتاج يتخزن وقت البلوك
```

---

## 5. PAYMENT WORKFLOW — منطق الدفع اليدوي

### 5.1 رحلة التاجر — Merchant Flow

```
1. التاجر يضغط "Pay & Close" من صفحة الفاتورة
2. لو القطع < 6 → Confirmation Modal:
      - تنبيه: رسوم +25ج/قطعة
      - الإجمالي بالرسوم
      - خياران: "أكمل التسوق" / "أكد الدفع بالرسوم"
3. اختيار نوع الدفع:
      - شحن: تأكيد العنوان + طريقة التواصل
      - استكمال: بدون رسوم (الرسوم عند الشحن الفعلي)
4. invoice_state → locked
5. صفحة الدفع: حسابات البنك + فودافون كاش + بريد + زر "انسخ"
6. التاجر يرفع screenshot التحويل + ملاحظة اختيارية  ← TODO
7. الفاتورة تنتظر تأكيد الإدارة (has_pending_payment = True) ← TODO
```

### 5.2 تأكيد الإدارة — Admin Confirmation

```
تأكيد ✅:
   → لو "شحن": invoice_state = 'paid' → الفاتورة تخرج للشحن
   → لو "استكمال": invoice_state = 'continuation' → عداد جديد يبدأ

رفض ❌:
   → invoice_state يفضل 'locked'
   → rejection_reason يتسجل على الـ SO  ← TODO
   → إشعار للتاجر: دائم على صفحة الفاتورة + مؤقت أعلى الموقع  ← TODO
   → التاجر يقدر يرفع screenshot جديد لنفس الفاتورة
   → العداد يكمل في الخلفية — لو عدى يوم 16 → blocked
```

### 5.3 الرسوم — Surcharge Rules

```
الشحن:   لو القطع < 6 → رسوم 25ج × عدد القطع كـ line item في الفاتورة
الاستكمال: بدون رسوم (الرسوم تُحسب فقط عند اختيار الشحن النهائي)

مثال: تاجر دفع استكمال على 4 قطع، أضاف قطعة 5، قرر يشحن
   → رسوم = 5 × 25 = 125 ج (مش 4 × 25)
```

---

## 6. UNIFIED INVOICE — الفاتورة الموحدة

لما التاجر يضيف منتج جديد، الـ logic يفحص الفواتير الموجودة بهذا الترتيب:

| الأولوية | الشرط | الإجراء |
|---|---|---|
| 🥇 1 | فاتورة `continuation` مفتوحة للإضافة | اضف عليها (لو إجمالي القطع < 20) |
| 🥈 2 | فاتورة `open` عادية | اضف عليها |
| 🆕 3 | لا شيء من دول | فاتورة جديدة `open` بعداد 10 أيام |

> ⚠️ لو الاتنين موجودين في نفس الوقت (`continuation` + `open`) → الأولوية للـ `continuation`.
> ⚠️ الأولوية رقم 1 تحتاج تنفيذ Continuation mode أولاً (Phase 2 في GAP_ANALYSIS.md).

---

## 7. DATABASE FIELDS — الحقول في الداتابيز

### على sale.order
| Field | Type | Description |
|-------|------|-------------|
| `invoice_open_date` | Datetime | تاريخ فتح الفاتورة (يوم الـ Confirm) |
| `invoice_deadline_date` | Datetime | تاريخ القفل (open_date + 10 أيام) — computed |
| `grace_end_date` | Datetime | تاريخ البلوك (open_date + 16 يوم) — computed |
| `invoice_state` | Selection | open / locked / grace / blocked / paid / continuation |
| `merged_into_so_id` | Many2one(sale.order) | الـ SO الموحَّد عليه (لو الـ SO الجديد اتدمج في موجود) |
| `total_pieces` | Float | عدد القطع الكلي (بدون line الرسوم) — computed |
| `is_below_minimum` | Boolean | True لو القطع بين 1 و 5 — computed |
| `minimum_fee_amount` | Float | الرسوم المحسوبة (قطع × 25) — computed |
| `paused_at` | Datetime | وقت البلوك (لحساب الأيام المتبقية عند فك البلوك) — **TODO** |
| `has_pending_payment` | Boolean | في دفعة في الانتظار (بعد رفع screenshot) — **TODO** |
| `payment_type` | Selection | shipping / continuation (اختيار وقت الدفع) — **TODO** |
| `rejection_reason` | Text | سبب رفض الدفع من الإدارة — **TODO** |

### على res.partner
| Field | Type | Description |
|-------|------|-------------|
| `is_blocked` | Boolean | العميل محظور بسبب فواتير غير مدفوعة |

> الحقول المعلَّمة **TODO** موجودة في المواصفات لكن لسه مش متعمَّلة في الكود.

---

## 8. WHAT'S DONE ✅ — اللي اتعمل

```
✅ 1.  تعطيل auto_confirm module (Uninstalled)
✅ 2.  إنشاء invoice_deadline module
✅ 3.  الحقول على sale.order (invoice_open_date, deadline, grace, state, total_pieces, fee)
✅ 4.  الحقل على res.partner (is_blocked)
✅ 5.  Cron Job يومي (open→locked→blocked + cascade)
✅ 6.  action_confirm يمنع البلوك
✅ 7.  تيست الـ Cron — شغال صح
✅ 8.  تيست منع الـ Confirm للعميل البلوك — شغال صح
✅ 9.  Unified Invoice — الـ SO الجديد بيتدمج في الموجود تلقائياً (priority #2)
✅ 10. Payment Closes Invoice — auto عبر account.move + manual button (Mark as Paid)
✅ 11. Backend UI — تاب على SO form + badge + عمود في list + banner partner
✅ 12. Website UI — alerts + countdown + block checkout للمحظور
✅ 13. Below-minimum surcharge — 25 EGP/piece كـ line item تلقائي
✅ 14. Customer-initiated lock — زر "Pay & Close" على portal
✅ 15. Payment info display — فودافون كاش + بريد + واتس على portal
✅ 16. Cascade unblock — action_mark_paid بتفك بلوك الـ siblings اللي في grace
```

---

## 9. WHAT'S REMAINING ⏳ — اللي لسه هنعمله

مرتَّب حسب خطة التنفيذ في `GAP_ANALYSIS.md`:

```
── Phase 1: Bug Fixes ──────────────────────────────────────────
⏳ JS Countdown — تحويل لـ Odoo module format (DOMContentLoaded issue)
⏳ action_confirm search condition — تصحيح لـ 'open' بس مش ('open','locked','grace')
⏳ paused_at field — إضافة + pause/resume logic بعد فك البلوك

── Phase 2: Grace State ─────────────────────────────────────────
⏳ Cron: إضافة locked → grace transition (يوم 11)
   [يحتاج قرار: هل grace يبدأ مع locked ولا بعده؟]

── Phase 3: 1000 EGP Penalty ───────────────────────────────────
⏳ product_penalty_1000 — إنشاء service product للغرامة
⏳ Cron: إضافة غرامة 1000ج تلقائياً على SO المبلوك
⏳ action_mark_paid — التحقق من دفع الغرامة قبل فك الحظر
⏳ Backend UI: إظهار total + غرامة على form الإدارة

── Phase 4: Payment Proof + Admin Workflow ─────────────────────
⏳ has_pending_payment flag على SO
⏳ Screenshot upload في portal (Odoo attachment)
⏳ خانة ملاحظة التاجر الاختيارية
⏳ Backend: قائمة "فواتير تنتظر التأكيد" (list filter)
⏳ زر "تأكيد الدفع" + زر "رفض الدفع" (بخانة سبب) في backend
⏳ rejection_reason field على SO
⏳ عرض سبب الرفض على portal page للتاجر (دائم)
⏳ In-app notification مؤقت عند الرفض

── Phase 5: Confirmation Modal ──────────────────────────────────
⏳ Modal HTML عند "Pay & Close" لو قطع < 6 (يعرض الرسوم + خيارين)

── Phase 6: Continuation Mode ───────────────────────────────────
⏳ payment_type field (shipping / continuation)
⏳ UI اختيار الشحن أو الاستكمال في صفحة الدفع
⏳ continuation state logic (عداد جديد، open للإضافة)
⏳ Max 20 pieces: auto-lock + notification
⏳ تحويل continuation → shipping (بدون العكس)
⏳ تعديل surcharge timing: تظهر فقط عند shipping
⏳ Unified Invoice Priority #1 (continuation أولوية)
⏳ رسالة "تواصل مع خدمة العملاء" لإلغاء فاتورة الاستكمال
```

---

## 10. OPEN QUESTIONS — أسئلة مفتوحة

```
❓ Grace State Trigger:
   متى بالضبط تتحول الفاتورة لـ grace؟
   → الخيار أ: Cron يوم 11 يحوّل مباشرة open → grace (بدل locked)
   → الخيار ب: open → locked (manual أو cron)، ثم locked → grace في يوم لاحق
   → الخيار ج: locked و grace هما نفس الحالة من وجهتين مختلفتين
   ← محتاج توضيح من نانسي

❓ Continuation counter:
   العداد الجديد (10 أيام) عند دخول continuation — هل صح منطقياً؟
   يعني الفاتورة ممكن تكون مفتوحة إجمالاً ~20 يوم.
   ← قرار مؤقت موثق في BUSINESS_LOGIC.md — محتاج تأكيد من نانسي
```

---

## 11. IMPORTANT NOTES — ملاحظات مهمة

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

6. الـ continuation state مش موجود في selection field بعد.
   لما تضيفه: لازم migration script عشان records القديمة.

7. الـ surcharge (below_minimum_fee) دلوقتي بتتحسب لايف على أي open SO.
   بعد تنفيذ Continuation: الرسوم تتصفر تلقائياً لو payment_type = 'continuation'.
```

---

## 12. WORKFLOW FOR CLAUDE CODE — طريقة الشغل

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

## 13. RELATED DOCUMENTS — الملفات المرجعية

| الملف | الغرض |
|---|---|
| `BUSINESS_LOGIC.md` | المرجع الرسمي لكل قرارات العمل — **أي تعارض، BL يكسب** |
| `GAP_ANALYSIS.md` | تحليل الفجوات + خطة التنفيذ بالـ phases |
| `README.md` | نظرة عامة للمطورين الجدد |

---

*Last updated: 2026-05-16 — updated lifecycle (6 states), payment workflow, unified invoice priority, removed Loyalty (Phase 2), added TODO fields*
*Developer: Sherif Taha*
*Project: BlueBee-Eg Odoo B2B E-commerce*
