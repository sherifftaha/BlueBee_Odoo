# 📋 BlueBee Business Logic
## منطق العمل التفصيلي لموقع BlueBee | BlueBee Site Detailed Business Logic

**آخر تحديث | Last updated:** 2026-06-05
**الحالة | Status:** Phase 1 — **كل القرارات الأساسية متجاوبة + كل الـ sub-flows اكتملت (00→06)، جاهز للـ handoff لـ Claude Design** | All core decisions answered + all sub-flows complete (00→06), ready for Claude Design handoff
**المرجع | Reference:** هذا الملف هو المرجع الرسمي لمنطق العمل، أي قرار تجاري لازم يكون موثق هنا | This file is the official business logic reference; any business decision must be documented here.

---

## 🎯 الهدف من الملف | Purpose

ده ملف **حي** بيوثق كل قرارات منطق العمل اللي اتفقنا عليها بين المطور (شريف) وصاحبة الشركة (نانسي) بخصوص موقع BlueBee. الملف ده هيستخدم في 3 أماكن:
This is a **living** document tracking all business logic decisions agreed between developer (Sherif) and owner (Nancy) for the BlueBee site. Used in 3 places:

1. **مرجع للتطوير:** Claude Code بيستخدمه عند تنفيذ الفيتشرز | Development reference: Claude Code uses it when implementing features
2. **مرجع للتصميم:** Claude Design بيستخدمه عند بناء الـ mockups | Design reference: Claude Design uses it when building mockups
3. **مرجع للنقاش:** أساس أي نقاش مع نانسي بخصوص تعديلات | Discussion reference: basis for any modification talk with Nancy

---

## 📑 المحتويات | Table of Contents

1. [حالات حساب التاجر](#1-حالات-حساب-التاجر--merchant-account-states)
2. [حالات الفاتورة](#2-حالات-الفاتورة--invoice-states)
3. [ثبات الفاتورة بعد التأكيد](#3-ثبات-الفاتورة-بعد-التأكيد--invoice-immutability)
4. [دفع الفاتورة](#4-دفع-الفاتورة--invoice-payment)
5. [نوعين الدفع: شحن vs استكمال](#5-نوعين-الدفع--two-payment-types)
6. [الحد الأدنى والرسوم](#6-الحد-الأدنى-والرسوم--minimum--surcharge)
7. [أولوية الفاتورة](#7-أولوية-الفاتورة--invoice-priority)
8. [سيناريو البلوك](#8-سيناريو-البلوك--block-scenario)
9. [إشعارات الرفض](#9-إشعارات-الرفض--rejection-notifications)
10. [إشعارات إعادة التوفر](#10-إشعارات-إعادة-التوفر--restock-notifications)
11. [تتبّع المخزون على مستوى الـ Variant](#11-تتبّع-المخزون-على-مستوى-الـ-variant--variant-level-stock-tracking)
12. [CSS Logical Properties](#12-css-logical-properties)
13. [نقاط محتاجة قرار من نانسي](#13-نقاط-محتاجة-قرار-من-نانسي--points-needing-nancys-decision)
14. [قرارات Phase 2](#14-قرارات-phase-2--phase-2-decisions)

---

## 1. حالات حساب التاجر | Merchant Account States

الـ `application_status` على الـ `res.partner` بياخد 4 قيم:
The `application_status` field on `res.partner` takes 4 values:

| الحالة State | المعنى Meaning | الـ Transition |
|---|---|---|
| `pending` 🟡 | الكونتاكت اتعمل + الطلب اتقدّم، مستني مراجعة الإدارة، مفيش portal access | عند تقديم الطلب |
| `pending` 🟡 | Contact created + application submitted, awaiting review, no portal access | On submit |
| `approved` 🔵 | الإدارة وافقت → grant portal access + invitation email + رسالة wa.me، لسه التاجر ماقبلش | `action_approve_application` من `pending` |
| `approved` 🔵 | Admin approved → portal access granted + invitation email + wa.me message, not yet accepted | `action_approve_application` from `pending` |
| `active` 🟢 | التاجر قبل الدعوة + عمل باسورد، يقدر يدخل الموقع | بعد إتمام الـ signup من `approved` |
| `active` 🟢 | Merchant accepted invite + set password, can access the site | After signup completion from `approved` |
| `rejected` 🔴 | الإدارة رفضت + سبب مكتوب | `action_reject_application` من `pending` |
| `rejected` 🔴 | Admin rejected + written reason | `action_reject_application` from `pending` |

### قاعدة الدخول | Auth Rule
- **التاجر مقدرش يعمل login إلا لو `application_status = active`**
- **A merchant cannot log in unless `application_status = active`**
- pending / approved / rejected → محاولة الدخول ترفض برسالة مناسبة
- pending / approved / rejected → login attempt rejected with appropriate message

### آلية التفعيل | Activation mechanism
- الموافقة بتعمل: (أ) grant portal access (إنشاء `res.users` بـ portal group)، (ب) Odoo يبعت invitation email، (ج) رسالة wa.me فيها نفس لينك الدعوة كـ fallback
- Approval triggers: (a) grant portal access (create `res.users` with portal group), (b) Odoo sends invitation email, (c) wa.me message with the same invite link as fallback
- التاجر يفتح اللينك → يعمل باسورد → الـ signup يحدّث `application_status = active` **كجزء من الـ flow قبل الـ auto-login** (عشان الـ auth gate ما يمنعش الدخول التلقائي بعد التفعيل)
- Merchant opens link → sets password → signup sets `application_status = active` **as part of the flow before auto-login** (so the gate doesn't block the post-activation auto-login)

> 💡 جمهورنا ٩٨٪ سيدات أصحاب محلات، مش كلهم بيتابعوا الإيميل — عشان كده لينك الدعوة في رسالة wa.me مهم كـ fallback عملي.
> 💡 98% of our audience are women shop owners who don't all check email — so the invite link inside the wa.me message matters as a practical fallback.

### العلاقة بالـ Onboarding | Relation to Onboarding
- `active` شرط مسبق لأول login. بعد أول دخول → الـ Onboarding (تأكيد البيانات gate + الجولة)، متحكّم فيه بـ `onboarding_completed` + `data_confirmed` (منفصلين عن `application_status`)
- `active` is the precondition for first login. After first login → Onboarding (data-confirm gate + tour), governed by `onboarding_completed` + `data_confirmed` (separate from `application_status`)

### الحقول المرتبطة | Related fields (من Sub-Flow #00)
`application_status`, `application_date`, `application_telegram_link`, `application_business_type`, `application_years_experience`, `application_rejection_reason`, `application_review_date`, `application_reviewed_by`
Methods: `action_approve_application` + `action_reject_application`

---

## 2. حالات الفاتورة | Invoice States

الـ `invoice_state` field على الـ `sale.order` بياخد 5 قيم:
The `invoice_state` field on `sale.order` takes 5 values:

| الحالة State | المعنى Meaning | الـ Transition |
|---|---|---|
| `open` 🟦 | الفاتورة مفتوحة، التاجر بيضيف منتجات بحرية، العداد بيشتغل (10 أيام) | إنشاء الفاتورة |
| `open` 🟦 | Invoice open, merchant adds products freely, counter runs (10 days) | On invoice creation |
| `locked` 🟧 | الفاتورة مقفولة للإضافة. بتحصل بطريقتين: (أ) عدى 10 أيام من غير دفع — تلقائي عبر cron، (ب) التاجر طلب دفع يدوياً | من `open` |
| `locked` 🟧 | Invoice closed for additions. Two triggers: (a) 10 days passed without payment — auto via cron, (b) merchant manually requested payment | From `open` |
| `grace` 🟨 | فترة سماح يوم 11-16. التاجر يقدر يفتح فاتورة #2 جديدة بعداد منفصل | من `locked` بعد 10 أيام |
| `grace` 🟨 | Grace period days 11-16. Merchant can open new Invoice #2 with separate counter | From `locked` after 10 days |
| `blocked` 🟥 | يوم 17، التاجر اتبلوك تماماً. كل الفواتير المفتوحة بتاعته تتقفل (cascade) | من `grace` يوم 17 |
| `blocked` 🟥 | Day 17, merchant fully blocked. All open invoices lock (cascade) | From `grace` on day 17 |
| `paid` 🟩 | الإدارة أكدت الدفع، الفاتورة قفلت نهائياً | من `locked` بعد تأكيد الإدارة |
| `paid` 🟩 | Admin confirmed payment, invoice permanently closed | From `locked` after admin confirmation |

### ملاحظة مهمة: الاستكمال flag مش state | Important: continuation is a flag, not a state

الاستكمال **مش حالة سادسة**. الفاتورة بتفضل `open` وبيتحط عليها flag `is_continuation = True`:
Continuation is **not a 6th state**. The invoice stays `open` with an `is_continuation = True` flag set on it:

- `is_continuation` (Boolean, default False) بيتعمل True عند تأكيد دفعة استكمال (قسم 5)
- `is_continuation` (Boolean, default False) set True on continuation-payment confirmation (Section 5)
- **السبب:** فاتورة الاستكمال بتعدّي بنفس دورة الحياة (لو عدّت 10 أيام → `locked` → `grace` → `blocked`/`paid`). الـ flag بيرافقها خلال الدورة كلها من غير انفجار حالات
- **Why:** a continuation invoice goes through the same lifecycle (10 days → `locked` → `grace` → `blocked`/`paid`). The flag rides along through the whole lifecycle without state explosion
- الـ flag بيفرّق في 3 حاجات بس: حد الـ 20 قطعة، أولوية الإضافة (قسم 7)، وريست عداد الـ deadline
- The flag changes only 3 things: the 20-piece cap, add priority (Section 7), and resetting the deadline counter

---

## 3. ثبات الفاتورة بعد التأكيد | Invoice Immutability

بعد ما التاجر يأكد الفاتورة، الفاتورة **immutable من جهة التاجر**:
After the merchant confirms, the invoice is **immutable from the merchant's side**:

- ❌ مفيش إلغاء فاتورة | No invoice cancellation
- ❌ مفيش تبديل قطعة بأخرى | No swapping one piece for another
- ❌ مفيش تخفيض كمية | No quantity reduction
- ✅ الإضافة مسموحة (حسب أولوية الفاتورة قسم 7 + حد الـ 20 في الاستكمال) | Adding is allowed (per priority Section 7 + 20-piece continuation cap)
- 🔧 أي تعديل تاني = خدمة عملاء يدوياً (واتس / تليفون) | Any other change = manual customer service (WhatsApp / phone)

### ⛔ قاعدة "ربع الساعة" — ملغاة | "Quarter-hour" rule — Abolished

سياسة الشركة القديمة كانت بتسمح بالإلغاء/التبديل خلال ربع ساعة من الاختيار. **القاعدة دي اتلغت تماماً** في النظام الجديد:
The old company policy allowed cancel/swap within 15 minutes of selection. **This rule is fully abolished** in the new system:

- مفيش نافذة زمنية للإلغاء الذاتي خالص
- No self-cancellation time window at all
- الثبات بيبدأ من لحظة التأكيد مباشرة
- Immutability starts immediately at confirmation
- السبب: تبسيط المنطق + تقليل الـ refunds + وضوح للتاجر
- Reason: simpler logic + fewer refunds + clarity for the merchant

---

## 4. دفع الفاتورة | Invoice Payment

### عملية الدفع | Payment process

1. التاجر يضغط "اطلب دفع" من الكارت أو صفحة الفاتورة
   Merchant clicks "Request Payment" from cart or invoice page
2. لو القطع أقل من 6 وقت الشحن، يظهر **Confirmation Modal** فيه:
   If < 6 pieces at shipping, **Confirmation Modal** shows:
   - تنبيه برسوم +25ج/قطعة
   - +25 EGP/piece surcharge warning
   - الإجمالي بالرسوم
   - Total with surcharge
   - خياران: "أكمل التسوق" / "أكد الدفع بالرسوم"
   - Two options: "Continue shopping" / "Confirm with surcharge"
3. الفاتورة تتقفل (`invoice_state = locked`)
   Invoice locks (`invoice_state = locked`)
4. صفحة الدفع: عرض حسابات بنك، فودافون كاش، بريد + زر "انسخ"
   Payment page: bank, Vodafone Cash, postal accounts + "Copy" button
5. التاجر يرفع سكرين شوت التحويل + ملاحظة اختيارية
   Merchant uploads transfer screenshot + optional note
6. الفاتورة تبقى في انتظار تأكيد الإدارة (الـ `locked` فيها flag إن في دفعة معلقة)
   Invoice awaits admin confirmation (`locked` has flag indicating pending payment)

### تأكيد الإدارة | Admin confirmation

**تأكدت ✅:**
**Confirmed ✅:**
- `invoice_state = paid`
- لو "شحن" → الفاتورة تخرج للشحن
- If "shipping" → invoice ships out
- لو "استكمال" → الفاتورة تفضل مفتوحة للإضافة لحد 20 قطعة (تفاصيل قسم 5)
- If "continuation" → invoice stays open for additions up to 20 (Section 5 details)

**رفضت ❌:**
**Rejected ❌:**
- الفاتورة تفضل `locked`
- Invoice stays `locked`
- إشعار للتاجر + سبب الرفض مكتوب
- Notification to merchant + written rejection reason
- التاجر يقدر يدفع تاني (يرفع سكرين تاني) لنفس الفاتورة
- Merchant can pay again (upload new screenshot) for same invoice
- العداد يكمل في الخلفية. لو عدى 16 يوم → `blocked`
- Counter continues in background. If past 16 days → `blocked`

---

## 5. نوعين الدفع | Two Payment Types

عند طلب الدفع، التاجر يختار **شحن** أو **استكمال**.
At payment request, merchant chooses **Shipping** or **Continuation**.

### 🚚 خيار 1: شحن (Shipping)

- التاجر يأكد العنوان وطريقة التواصل
- Merchant confirms address and contact method
- يطبق الحد الأدنى 6 قطع + رسوم +25ج/قطعة لو ناقص (تفاصيل قسم 6)
- Minimum 6 pieces + 25 EGP/piece surcharge if short (Section 6)
- دفعة واحدة شاملة (تمن القطع + رسوم لو في)
- One inclusive payment (piece price + surcharge if any)
- بعد تأكيد الإدارة → `paid` → الفاتورة تخرج للشحن
- After admin confirmation → `paid` → invoice ships out

### 🔁 خيار 2: استكمال (Continuation)

**القاعدة الذهبية:** التاجر يحجز قطع، يدفع تمنها بسعرها الأصلي **بدون رسوم**، الفاتورة تفضل مفتوحة لإضافة قطع تاني، لحد ما يقرر يحول لشحن.
**Golden rule:** Merchant books pieces, pays for them at original price **without surcharge**, invoice stays open for adding more pieces, until deciding to switch to shipping.

**التفاصيل | Details:**

- التاجر يدفع تمن القطع المحجوزة بسعرها الأصلي
- Merchant pays for booked pieces at original price
- **بدون رسوم +25ج** (الرسوم تتطبق فقط وقت الشحن النهائي لو ناقص)
- **No +25 EGP surcharge** (applies only at final shipping if short)
- عند تأكيد دفعة الاستكمال: `is_continuation = True` + ريست تاريخ الـ deadline (عداد 10 أيام جديد)
- On continuation-payment confirmation: `is_continuation = True` + reset deadline date (new 10-day counter)
- الفاتورة تفضل في حالة الإضافة بعد تأكيد دفع الاستكمال
- Invoice stays in addition mode after continuation payment confirmation
- **الحد الأقصى: 20 قطعة إجمالي** (مش فوق الـ 6 الأصلية)
- **Maximum: 20 pieces total** (not beyond original 6)
- لما يوصل 20 → الفاتورة تقفل تلقائياً + إشعار "وصلت للحد الأقصى، الفاتورة هتتشحن"
- At 20 → invoice auto-locks + notification "max reached, will ship"
- التاجر يقدر يحول من استكمال لشحن في أي وقت ⚠️ **مش العكس** (الشحن قرار نهائي)
- Merchant can switch continuation→shipping anytime ⚠️ **not reverse** (shipping is final)

**عداد الـ 10 أيام في الاستكمال | 10-day counter in continuation:**
عند دخول وضع الاستكمال، **عداد جديد 10 أيام يبدأ من الأول** (مش بيكمل من القديم).
On entering continuation mode, **new 10-day counter restarts** (doesn't continue from old).

> ⚠️ **ملاحظة:** ده قرار مؤقت، محتاج مراجعة مع نانسي للتأكد من المنطق التجاري.
> ⚠️ **Note:** This is a tentative decision, needs review with Nancy to confirm business logic.

---

### 🚫 سياسة إلغاء فاتورة الاستكمال | Continuation Cancellation Policy

**القاعدة:** بعد ما التاجر يدفع دفعة استكمال، **مفيش إلغاء ذاتي من الموقع**. ⛔
**Rule:** After merchant pays a continuation payment, **no self-cancellation from the site**.

- التاجر يقدر يستمر في الإضافة أو يحول لشحن
- Merchant can continue adding or switch to shipping
- لو عايز يلغي → **لازم يتواصل مع خدمة العملاء مباشرة** (واتس / تليفون)
- If wants to cancel → **must contact customer service directly** (WhatsApp / phone)
- الإلغاء (لو الإدارة وافقت) قرار يدوي من الإدارة، مش زرار في الموقع
- Cancellation (if admin approves) is a manual admin action, not a site button

**ليه؟ | Why?**
- لتقليل احتمال الـ refunds وتعقيدها
- To reduce refund probability and complexity
- التواصل المباشر بيخلي الإدارة تتفاهم مع التاجر (يمكن توجهه لاستكمال بدل إلغاء)
- Direct contact lets admin negotiate with merchant (may redirect to continuation instead of cancel)

---

## 6. الحد الأدنى والرسوم | Minimum & Surcharge

### القاعدة الأساسية | Base rule

- الحد الأدنى للشحن: **6 قطع**
- Minimum for shipping: **6 pieces**
- لو أقل من 6 وقت الشحن → رسوم **25ج/قطعة**
- If < 6 at shipping → **25 EGP/piece** surcharge

### التطبيق في الـ Continuation | Application in continuation

الرسوم تتطبق **وقت الشحن الفعلي**، مش وقت الاستكمال. أمثلة:
Surcharge applies **at actual shipping**, not at continuation. Examples:

**مثال 1 | Example 1:**
- التاجر حجز 4 قطع وعمل استكمال
- Merchant booked 4 pieces, chose continuation
- يدفع تمن الـ 4 قطع بس (بدون رسوم) + تنبيه بالحد الأدنى
- Pays for 4 pieces only (no surcharge) + minimum warning
- ضاف قطعة خامسة في الاستكمال = 5 قطع
- Added 5th piece in continuation = 5 pieces
- قرر يشحن → يدفع 25ج × 5 = **125ج رسوم**
- Decides to ship → pays 25 × 5 = **125 EGP surcharge**

**مثال 2 | Example 2:**
- التاجر حجز 4 قطع وعمل استكمال، ومضافش حاجة
- Merchant booked 4 pieces, chose continuation, added nothing
- قرر يشحن بالـ 4 قطع → يدفع 25ج × 4 = **100ج رسوم**
- Decides to ship with 4 → pays 25 × 4 = **100 EGP surcharge**

**مثال 3 | Example 3:**
- التاجر حجز 8 قطع وعمل استكمال
- Merchant booked 8 pieces, chose continuation
- قرر يشحن → **مفيش رسوم** (لإنه فوق 6)
- Decides to ship → **no surcharge** (above 6)

### عرض الرسوم في الفاتورة | Surcharge display

الرسوم تظهر كـ **line item داخل الفاتورة** عند تأكيد الشحن (transparency):
Surcharge shows as **line item inside invoice** at shipping confirmation (transparency):

```
3 × طقم بيتي قطن (4 سنة) ........... 255 ج
2 × فانلة قطن (6 سنة) ............... 90 ج
─────────────────────────────────────────
رسوم أقل من الحد الأدنى (5 قطع) ..... 125 ج
─────────────────────────────────────────
الإجمالي ............................ 470 ج
```

---

## 7. أولوية الفاتورة | Invoice Priority

لما التاجر يضيف منتج جديد لكارته، الـ logic بيشوف فواتيره الـ `open` بالترتيب ده:
When merchant adds a new product, logic checks his `open` invoices in this order:

1. 🥇 فاتورة `open` بـ `is_continuation = True` → اضف عليها (أولوية أولى)
   `open` invoice with `is_continuation = True` → add to it (first priority)
2. 🥈 فاتورة `open` عادية (`is_continuation = False`) → اضف عليها
   Regular `open` invoice (`is_continuation = False`) → add to it
3. 🆕 مفيش فاتورة open → فاتورة جديدة `open` بعداد 10 أيام
   No open invoice → new `open` invoice with 10-day counter

⚠️ **مهم:** لو في فاتورة استكمال + فاتورة open عادية في نفس الوقت، الأولوية لفاتورة الاستكمال.
⚠️ **Important:** If both a continuation invoice and a regular open invoice exist simultaneously, the continuation invoice takes priority.

---

## 8. سيناريو البلوك | Block Scenario

### الـ Cascade Lock

لما التاجر يوصل يوم 17 من غير دفع لأي فاتورة معلقة:
When merchant reaches day 17 without paying any pending invoice:

- كل الفواتير المفتوحة بتاعته → `blocked`
- All his open invoices → `blocked`
- الـ `is_blocked = True` على الـ `res.partner`
- `is_blocked = True` on `res.partner`
- التاجر مايقدرش يفتح فواتير جديدة
- Merchant cannot open new invoices
- التاجر يشوف رسالة الحظر في كل صفحة + زر واتس للدعم
- Merchant sees block message on every page + WhatsApp support button

### غرامة الـ 1000 جنيه | 1000 EGP Penalty

- لما التاجر يتبلوك بسبب عدم الدفع
- When merchant gets blocked for non-payment
- يدفع: الفاتورة الأصلية + **غرامة 1000 جنيه**
- Pays: original invoice + **1000 EGP penalty**
- **الإدارة بتشيل الحظر يدوياً** بعد تأكيد دفع الغرامة + الفاتورة
- **Admin manually lifts block** after confirming penalty + invoice payment
- مش بيتفك الحظر تلقائياً
- Not auto-lifted

### فاتورة #2 بعد فك البلوك | Invoice #2 after unblock

السيناريو: التاجر عنده فاتورة #1 معلقة من يوم 1، وفاتورة #2 بدأها في يوم 12 (في فترة الـ grace) ولسه فاضل ليها 7 أيام. عدى يوم 17 → الاتنين اتبلوكوا.
Scenario: merchant has Invoice #1 pending since day 1, started Invoice #2 on day 12 (grace) with 7 days remaining. Day 17 hit → both blocked.

**القرار:** بعد فك البلوك، **فاتورة #2 تكمل من اليوم اللي وقفت فيه** (الـ 7 أيام المتبقية).
**Decision:** After unblock, **Invoice #2 resumes from where it stopped** (the 7 remaining days).

> 💡 **تطبيق تقني:** لازم نخزن `paused_at` timestamp على الفاتورة وقت البلوك، ونحسب الـ remaining_days وقت فك البلوك.
> 💡 **Technical implementation:** Must store `paused_at` timestamp on invoice at block, calculate `remaining_days` at unblock.

---

## 9. إشعارات الرفض | Rejection Notifications

لما الإدارة ترفض دفع، التاجر يشوف سبب الرفض في:
When admin rejects payment, merchant sees rejection reason in:

| المكان Location | الطبيعة Nature | متى Phase |
|---|---|---|
| 📄 صفحة الفاتورة نفسها | دائم، يفضل ظاهر لحد ما يدفع تاني | Phase 1 |
| 📄 Invoice page itself | Permanent, visible until paying again | Phase 1 |
| 🔔 Notification في الموقع | مؤقت، تظهر أعلى الصفحة | Phase 1 |
| 🔔 Site notification | Temporary, appears at top of page | Phase 1 |
| 📱 Push notification على الموبايل | يتطلب الموقع PWA | **Phase 2** |
| 📱 Mobile push notification | Requires site to be PWA | **Phase 2** |

---

## 10. إشعارات إعادة التوفر | Restock Notifications

لما منتج (variant معين: مقاس + لون) يبقى out-of-stock تماماً، التاجر يقدر يطلب إشعار لما يرجع متاح.
When a product (specific variant: size + color) is fully out-of-stock, the merchant can request a notification when it's back.

### الموديل | Model: `product.notify.request`

| الحقل Field | النوع Type | الوصف Description |
|---|---|---|
| `partner_id` | Many2one (`res.partner`) | التاجر اللي طلب / Requesting merchant |
| `product_id` | Many2one (`product.product`) | الـ variant المطلوب مش الـ template / Variant, not template |
| `request_date` | Datetime | تاريخ الطلب / Request date |
| `state` | Selection | `waiting` / `notified` / `cancelled` |
| `notified_date` | Datetime | تاريخ إرسال الإشعار / When notified |

### المنطق | Logic
- زر "بلغني لما يتوفر" يظهر على الـ variant الـ out-of-stock فقط
- "Notify me when available" appears only on the out-of-stock variant
- نفس التاجر + نفس الـ variant = طلب واحد (unique constraint)
- Same merchant + same variant = one request (unique constraint)
- لما المخزون يرجع > 0 على الـ variant → الإشعار يتبعت + `state = notified`
- When variant stock returns > 0 → notification sent + `state = notified`
- الإشعار in-app في Phase 1 — الـ Push مؤجل لـ Phase 2
- In-app in Phase 1 — Push deferred to Phase 2
- ⚠️ الإشعار مش حجز: المنتج ممكن يخلص تاني قبل ما التاجر يطلب
- ⚠️ Notification is not a reservation: product may sell out again before the merchant orders

---

## 11. تتبّع المخزون على مستوى الـ Variant | Variant-Level Stock Tracking

المخزون بيتتبّع على مستوى الـ **variant** (`product.product` = مقاس + لون)، مش على مستوى الـ template (`product.template`).
Stock is tracked at the **variant** level (`product.product` = size + color), not the template level (`product.template`).

### القواعد | Rules
- كل تركيبة مقاس + لون ليها مخزون مستقل
- Each size + color combination has independent stock
- **مفيش stock check في الـ frontend ولا في الكارت** (Stock Enumeration Prevention)
- **No stock check in frontend or cart** (Stock Enumeration Prevention)
- الـ check الوحيد عند **Confirm** فقط
- The only check is at **Confirm**
- لو الكمية المطلوبة أكتر من المتاح → رسالة "الكمية المتوفرة أقل" **بدون أرقام**
- If requested qty > available → message "available quantity is lower" **without numbers**
- Cart smart refresh يبان فقط للـ variants الـ out-of-stock تماماً (مش الكميات الجزئية)
- Cart smart refresh shows only for fully out-of-stock variants (not partial quantities)

---

## 12. CSS Logical Properties

عشان الموقع bilingual (عربي RTL / إنجليزي LTR)، استخدام الـ **CSS Logical Properties إجباري** في كل الـ layout.
Because the site is bilingual (Arabic RTL / English LTR), using **CSS Logical Properties is mandatory** across all layout.

### القاعدة | Rule
استخدم الـ logical properties بدل الـ physical:
Use logical properties instead of physical:

| ❌ ممنوع Physical | ✅ مطلوب Logical |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left` / `right` | `inset-inline-start` / `inset-inline-end` |
| `text-align: left` | `text-align: start` |
| `border-left` | `border-inline-start` |

- ده بيخلي الـ layout يقلب تلقائياً مع تغيير اللغة من غير CSS منفصل لكل اتجاه
- This makes the layout flip automatically with language change, no separate CSS per direction
- ينطبق على Claude Design (الـ prototypes) و Claude Code (تنفيذ Odoo)
- Applies to both Claude Design (prototypes) and Claude Code (Odoo implementation)

---

## 13. نقاط للتأكيد مع نانسي (مش بلوكر) | Points to Confirm with Nancy (Non-blocking)

كل القرارات الأساسية اتجاوبت. النقاط دي للتأكيد بس، الـ Phase 1 يقدر يكمل من غيرها:
All core decisions answered. These points are for confirmation only; Phase 1 can proceed without them:

### 🔄 نقاط للمراجعة عند مقابلة نانسي

**ت1.** عداد الـ 10 أيام في فاتورة الاستكمال — قرارنا **يبدأ من الأول** عند دخول الاستكمال. لو نانسي شافت إن ده هيخلي الفاتورة مفتوحة فترة طويلة (لحد 20 يوم تقريباً)، نقدر نراجع.
C1. 10-day counter on continuation invoice — our decision is **restart** when entering continuation. If Nancy feels this keeps invoice open too long (up to ~20 days), we can revisit.

**ت2.** الـ Loyalty system — مؤجل لـ Phase 2. نوضح لها إنه قرار محسوب لتسريع الإطلاق وإن البيانات الحقيقية هتساعد في تصميم أفضل.
C2. Loyalty system — deferred to Phase 2. Explain it's a calculated decision for faster launch and real data will help design it better.

**ت3.** PWA + Push notifications — مؤجلة لـ Phase 2. Phase 1 يحتوي in-app notifications + email بس.
C3. PWA + Push notifications — deferred to Phase 2. Phase 1 has in-app notifications + email only.

### ✅ نقاط اتقفلت بالفعل (للتوثيق فقط)

- **سيناريو SO #2 بعد فك البلوك:** تكمل من اليوم اللي وقفت فيه (موثق في قسم 8)
- **SO #2 after unblock scenario:** Resumes from where it stopped (documented in Section 8)
- **غرامة الـ 1000 جنيه:** تُدفع + الإدارة تشيل الحظر يدوياً (موثق في قسم 8)
- **1000 EGP penalty:** Paid + admin manually lifts block (documented in Section 8)
- **إلغاء فاتورة الاستكمال:** مفيش إلغاء ذاتي، التاجر يتواصل مع خدمة العملاء مباشرة (موثق في قسم 5)
- **Continuation invoice cancellation:** No self-cancel, merchant contacts customer service directly (documented in Section 5)
- **حالات حساب التاجر:** 4 حالات (pending/approved/active/rejected) + قاعدة الدخول (موثق في قسم 1)
- **Merchant account states:** 4 states (pending/approved/active/rejected) + auth rule (documented in Section 1)
- **الاستكمال flag مش state:** `is_continuation` على فاتورة `open` (موثق في قسم 2)
- **Continuation is a flag not a state:** `is_continuation` on an `open` invoice (documented in Section 2)

---

## 14. قرارات Phase 2 | Phase 2 Decisions

الحاجات اللي قررنا نأجلها لما الموقع يثبت وعنده مستخدمين حقيقيين:
Things deferred until the site stabilizes with real users:

| الفيتشر Feature | السبب Reason |
|---|---|
| 🏆 نظام الـ Loyalty (برونزي/فضي/ذهبي) | محتاج بيانات حقيقية للمشتريات، أحسن يطبق بعد ما الموقع يبقى عنده تجار نشطين |
| 🏆 Loyalty system (bronze/silver/gold) | Needs real purchase data, better applied after site has active merchants |
| 📱 PWA + Push notifications | بنية تحتية معقدة (Service Worker, FCM)، تضيف 3-5 أيام على Phase 1 |
| 📱 PWA + Push notifications | Complex infrastructure (Service Worker, FCM), adds 3-5 days to Phase 1 |
| 💬 WhatsApp Business API integration | Phase 1 بيستخدم لينك واتس بسيط، API integration يجي لاحقاً |
| 💬 WhatsApp Business API integration | Phase 1 uses simple WhatsApp link, API integration comes later |
| 🔒 منطق الاحتكار (Hoarding) المتقدم | الإدارة قررت النظام الحالي + حد أقصى لقيمة الفاتورة + 10 أيام، يُحسم لاحقاً |
| 🔒 Advanced hoarding logic | Admin chose current system + max invoice value cap + 10 days, decided later |

---

## 📝 سجل التعديلات | Change Log

| التاريخ Date | التعديل Change | المسؤول By |
|---|---|---|
| 2026-05-16 | إنشاء الملف الأول | Sherif + Claude (chat) |
| 2026-05-16 | Initial file creation | Sherif + Claude (chat) |
| 2026-05-16 | تأكيد قرارات: عداد الاستكمال، تأجيل Loyalty، سياسة الإلغاء | Sherif |
| 2026-05-16 | Confirmed: continuation counter, Loyalty deferral, cancellation policy | Sherif |
| 2026-06-05 | اكتمال كل الـ sub-flows (00→06) | Sherif + Claude (chat) |
| 2026-06-05 | All sub-flows complete (00→06) | Sherif + Claude (chat) |
| 2026-06-05 | إضافة أقسام: حالات حساب التاجر، ثبات الفاتورة + إلغاء قاعدة ربع الساعة، إشعارات إعادة التوفر، تتبّع المخزون variant-level، CSS Logical Properties | Sherif + Claude (chat) |
| 2026-06-05 | Added sections: merchant account states, invoice immutability + quarter-hour abolition, restock notifications, variant-level stock, CSS Logical Properties | Sherif + Claude (chat) |
| 2026-06-05 | قرار: الاستكمال flag (`is_continuation`) مش state مستقلة — دورة الحياة تفضل 5 حالات | Sherif |
| 2026-06-05 | Decision: continuation is a flag (`is_continuation`), not a separate state — lifecycle stays 5 states | Sherif |
| 2026-06-05 | إعادة ترقيم الملف كامل (14 قسم) + تظبيط الـ cross-references | Sherif + Claude (chat) |
| 2026-06-05 | Full file renumber (14 sections) + cross-reference fixes | Sherif + Claude (chat) |

---

## 🔗 الملفات المرتبطة | Related Files

- `CLAUDE.md` — توثيق تقني للـ module
- `CLAUDE.md` — technical module documentation
- `LEARNING_PLAN.md` — خطة التعلم
- `LEARNING_PLAN.md` — learning plan
- `DEMO_WALKTHROUGH.md` — جولة تجريبية
- `DEMO_WALKTHROUGH.md` — demo walkthrough
- `flows/00_landing_and_application.md` … `flows/06_onboarding.md` — الـ 7 sub-flows
- `flows/00_landing_and_application.md` … `flows/06_onboarding.md` — the 7 sub-flows

## 🗺️ الرسومات التوضيحية | Visual Diagrams

المشروع له رسمتين متكاملتين موثقتين في الشات:
The project has two complementary diagrams documented in chat:

**1. Master Flow (Happy Path):** بتوضح رحلة التاجر من الدخول لاستلام البضاعة. مفيش تفاصيل الـ deadlines.
Master Flow: shows merchant journey from entry to delivery. No deadline details.

**2. State Transitions Flow:** بتوضح انتقالات حالات الفاتورة الـ 5 (open/locked/grace/blocked/paid) مع الـ triggers (manual vs cron) والـ deadlines (10 يوم، 16 يوم). الاستكمال بيظهر كـ flag (`is_continuation`) على حالة `open`، مش كحالة منفصلة.
State Transitions Flow: shows the 5 invoice states transitions with triggers (manual vs cron) and deadlines (10-day, 16-day). Continuation appears as a flag (`is_continuation`) on the `open` state, not a separate state.

الـ Master Flow بيخدم تصميم الـ UX، الـ State Transitions Flow بيخدم تنفيذ الكود.
Master Flow serves UX design, State Transitions Flow serves code implementation.

> 📌 **مقترح للـ handoff:** رسمة تالتة لـ **Merchant Account State Machine** (pending → approved → active / rejected) تكمّل البكدج لـ Claude Design.
> 📌 **Suggested for handoff:** a third diagram for the **Merchant Account State Machine** (pending → approved → active / rejected) to complete the bundle for Claude Design.

---

**End of document | نهاية الملف**
