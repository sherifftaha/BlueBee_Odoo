# 🎬 DEMO WALKTHROUGH — invoice_deadline
## دليل العرض المبدئي للعميل

> **الهدف:** ديمو 15-20 دقيقة، مرتب، احترافي، يخلي العميل يقول "نعم ده اللي عايزه".
> **القاعدة الذهبية:** اعرض الـ **VALUE** مش الـ FEATURES. كل خطوة قول "ده بيحلّ مشكلة كذا".

---

## 📋 PART 1 — تحضيرات قبل العرض بـ 15 دقيقة

### A) نظف الداتا (Clean DB state)

شغّل الأوامر دي عشان تبدأ بحالة نضيفة:

```bash
# 1. تأكد إن العميل التجريبي Hany مش مبلوك
docker compose exec db psql -U odoo -d odoo -c "UPDATE res_partner SET is_blocked = false WHERE id = 46;"

# 2. شيل أي SOs قديمة لـ Hany عشان نبدأ من الصفر (احذف الـ draft)
docker compose exec db psql -U odoo -d odoo -c "DELETE FROM sale_order WHERE id = 57 AND state = 'draft';"

# 3. خلي Hany عنده SO واحد بس في حالة (paid) عشان نوريها كـ "تاريخ سابق"
#    خلي S00047 = paid, S00052 = نخليه open للعرض
docker compose exec db psql -U odoo -d odoo -c "UPDATE sale_order SET invoice_state = 'paid' WHERE id = 47;"
docker compose exec db psql -U odoo -d odoo -c "UPDATE sale_order SET invoice_state = 'open' WHERE id = 52;"

# 4. تأكد إن في عميل تاني مبلوك للديمو (Partner 26 عنده SO blocked)
docker compose exec db psql -U odoo -d odoo -c "UPDATE res_partner SET is_blocked = true WHERE id = 26;"

# 5. Restart عشان كل حاجة تيجي طازة
docker compose restart odoo
```

### B) جهّز الـ Browser Tabs

| Tab | Purpose | URL |
|-----|---------|-----|
| 1 | عميل عادي (Hany) — Customer journey | `http://localhost:8069/shop` |
| 2 | Admin (Mitchell) — Backend | `http://localhost:8069/odoo/sales` |
| 3 | عميل مبلوك (Partner 26) — للسيناريو الأخير | جاهز للـ login |
| 4 | Terminal مفتوح — للحالات الطارئة | `cd "C:\Users\Sherif Taha\Desktop"` |

### C) Login Credentials (تأكد إنها شغالة)

| Account | Email | Password | Use |
|---------|-------|----------|-----|
| Hany | taaskm@gmail.com | test1234 | عميل عادي |
| Mitchell | admin | admin | Admin/Backend |

### D) جهّز موبايلك

- WhatsApp مفتوح — هتعرض الزرار يفتح رسالة فعلية
- Screen mirroring لو متاح (أحلى)

### E) ✅ Pre-flight Checklist (دقيقة قبل ما تبدأ)

- [ ] الـ Server شغال — `http://localhost:8069` بيفتح
- [ ] Hany مش مبلوك (banner مش ظاهر)
- [ ] Hany عنده SO `paid` واحد + كارت فاضي
- [ ] Partner 26 مبلوك
- [ ] Browser zoom 110%-125% (الناس تشوف)
- [ ] قفل أي tabs/notifications شخصية
- [ ] فاتح الـ DEMO_WALKTHROUGH ده على شاشة جانبية

---

## 🎤 PART 2 — افتتاحية (1 دقيقة)

**اللي تقوله بالظبط:**

> "BlueBee بيبيع جملة للتجار، بالأجل. المشكلة: إزاي تتحكم في مواعيد السداد بدون ما تطارد العملاء يدوياً؟ الـ module ده بيحلها بثلاث حاجات:
> 1. **Deadline تلقائي** — كل فاتورة عندها 10 أيام للدفع، بعدها 6 أيام سماح، بعدها بلوك تلقائي.
> 2. **Self-service للعميل** — العميل يشوف فواتيره، يدفع، يبعت إثبات بكليك.
> 3. **بلوك ذكي** — العميل المتأخر مش بس بيتمنع من الـ checkout، بيتمنع من تصفح الموقع أصلاً.
> خليني أوريك."

---

## 🎬 PART 3 — الديمو الكامل

### ACT 1 — رحلة العميل (Customer Journey) ⏱ 6 دقايق

**Tab 1 — Hany مسجل دخول**

#### 1.1 الـ Shop العادي
- روح `/shop`
- **قول:** "ده الموقع العادي للعميل المسجل."
- اختار منتج، اضغط على المنتج

#### 1.2 الزرار المعدل: "Add to Invoice"
- **اِلفت نظرهم:** "لاحظ الزرار مش 'Add to Cart' — هو **'Add to Invoice'**. ده مقصود — في B2B مفيش 'Cart' بمعنى التسوق، في **فاتورة جارية**."
- اضغط Add to Invoice → Modal يظهر بنفس الـ wording

#### 1.3 السلة → الفاتورة
- روح My Cart
- **قول:** "هنا برضه الزرار 'Add to Invoice' — العميل بيضيف للفاتورة، مش بيدفع دلوقتي."
- اضغط الزرار

#### 1.4 ⭐ AHA Moment 1: صفحة الفاتورة + العداد
- العميل بيتنقل لصفحة الـ portal SO
- في **green banner** "تم إضافة المنتجات على فاتورتك بنجاح"
- في **invoice status card** فيها:
  - Badge: `مفتوحة — Open`
  - تاريخ آخر موعد للسداد
  - **عداد LIVE بيعد التنازلي** (هز عينك على العداد!)
- **قول:** "العداد ده بيشتغل لايف في المتصفح. العميل عارف بالظبط فاضله أد إيه."

#### 1.5 ⭐ AHA Moment 2: Unified Invoice
- ارجع للـ shop، ضيف منتج تاني
- روح My Cart → Add to Invoice
- **اِلفت نظرهم:** "العميل ضاف منتج تاني — لكن مفتحش فاتورة جديدة. اتدمج على نفس الفاتورة الموجودة!"
- **قول:** "ده اسمه **Unified Invoice** — عندك عميل بيشتري على مدار 10 أيام، كله بيتجمع في فاتورة واحدة. مفيش تشتيت."

#### 1.6 My Invoices في الـ Navbar
- اضغط **"My Invoices"** في الـ navbar (جنب My Cart)
- **قول:** "كل فواتير العميل في مكان واحد — كل واحدة عداد لوحدها وحالة لوحدها. ده مهم لأن العميل ممكن يكون عنده فاتورة قفلت للدفع وفاتورة تانية مفتوحة لسه."

#### 1.7 ⭐ AHA Moment 3: Pay & Close Invoice
- ارجع للفاتورة المفتوحة
- اضغط **"دفع وتقفيل الفاتورة"**
- اظهر الـ **confirmation dialog** ("هل أنت متأكد؟ لن تتمكن من إضافة منتجات أخرى...")
- **قول:** "العميل بيقفل الفاتورة بنفسه لما يخلص شراء، فيها confirmation عشان مش يضغط بالغلط."
- أكد

#### 1.8 ⭐ AHA Moment 4: Payment Methods + WhatsApp
- الصفحة بتتحدث:
  - Badge: `مقفولة — Locked`
  - **Payment methods card** ظهرت: Vodafone Cash، البريد، المبلغ، رقم الفاتورة
  - زرار **WhatsApp** أخضر
- **اِلفت نظرهم:** الأرقام دي **placeholders** — قول صراحة:
  > "الأرقام دي مؤقتة، لما تديني أرقامك الحقيقية هتتغير من الـ Settings مباشرة بدون كود."
- اضغط زرار **"إرسال إثبات الدفع على واتساب"**
- WhatsApp يفتح بـ **رسالة محضرة فيها:**
  - اسم العميل
  - رقم الفاتورة
  - المبلغ
  - حقول فاضية للعميل يملاها (رقم العملية، طريقة الدفع)
- **قول:** "العميل مش هيكتب حاجة من نفسه — كله جاهز. هو بس بيدخل رقم العملية ويبعت."

---

### ACT 2 — جانب الـ Admin ⏱ 4 دقايق

**Tab 2 — Mitchell مسجل دخول**

#### 2.1 List View
- روح Sales → Orders
- **اِلفت نظرهم:** عمود `Invoice State` فيه badges ملونة (open/locked/paid/blocked)
- **قول:** "الـ Sales team بيشوف فوراً مين فاضل عليه دفع، مين دفع، مين مبلوك."

#### 2.2 SO Form — Invoice Deadline Tab
- افتح SO اللي العميل قفلها قبل شوية
- روح تاب **"Invoice Deadline"**
- اعرض:
  - **Timeline:** Open Date / Deadline Date / Grace End Date
  - **Status:** Badge بحالة الفاتورة
  - زرار **"Mark as Paid — تسجيل كمدفوعة"**

#### 2.3 ⭐ Mark as Paid Flow
- اضغط Mark as Paid
- **Confirmation dialog عربي/إنجليزي يظهر**
- أكد
- البادج بتتغير لـ `Paid`
- **قول:** "لو العميل دفع نقدي أو في الفرع، الـ Sales rep بيضغط الزرار، الفاتورة بتتقفل، ولو ده آخر فاتورة مبلوكة على العميل — بيترفع البلوك تلقائياً."

#### 2.4 Unmark Paid (لو دوست غلط)
- في زرار **"Unmark Paid — إلغاء الدفع"** بيظهر بعد ما تقفلها
- **قول:** "لو حد دوس غلط، فيه زرار يرجّع الفاتورة لحالتها حسب التاريخ الحالي."

---

### ACT 3 — سيناريو العميل المبلوك ⏱ 3 دقايق

**Tab 3 — Logout من Hany، login بعميل مبلوك**

> أو الأسهل: افتح Incognito وادخل بحساب Partner 26

#### 3.1 محاولة دخول الـ Shop
- روح `/shop`
- **اِلفت نظرهم:** الـ URL اتغير لـ `/shop/blocked` تلقائياً
- اعرض صفحة "حسابك محظور" بالـ design الاحترافي
- **قول:** "العميل المتأخر مش بنخليه يتصفح، نوضح له المشكلة وإزاي يحلها."

#### 3.2 Banner في الـ Backend
- ارجع لـ Tab 2 (Admin)
- افتح Partner 26
- اعرض الـ **red banner** "Blocked - Unpaid Invoices" فوق الفورم
- اعرض الـ **toggle** في تاب Sales & Purchase
- **قول:** "الـ Sales rep يقدر يفك البلوك يدوياً من هنا، أو لو العميل دفع، بيتفك تلقائياً."

---

### ACT 4 — الـ Automation (الـ Cron) ⏱ 1 دقيقة

> ⚠️ **متشغّلش الـ cron لايف في الديمو** — اشرح بس.

**قول:**
> "كل يوم منتصف الليل، النظام بيشتغل تلقائياً:
> - أي فاتورة عدّى عليها 10 أيام مفتوحة → بتتقفل (locked)
> - أي فاتورة قعدت 16 يوم بدون دفع → العميل بيتبلك تلقائياً، وكل فواتيره التانية بتتبلك معاها.
> - أنت متعملش حاجة، النظام بيمشّي نفسه."

اعرض في Settings → Technical → Scheduled Actions الـ cron name لو طلبوا يشوفوه (اختياري).

---

## 🚫 PART 4 — حاجات تتجنبها في الديمو

| ❌ متعرضش | السبب |
|-----------|--------|
| Payment auto-detection (account.move) | لسه ما اتختبرش، ممكن يطلع غلط قدامهم |
| الـ S00048 cancelled record | record قديم من اختبارات قديمة |
| تشغيل الـ cron لايف | لو في غلط في الداتا هيظهر قدامهم |
| ذكر "TODO" أو "remaining" | ركز على اللي شغال، الباقي تفاصيل |
| فتح الـ logs/terminal أمامهم | غير محترف، خلي الديمو visual |

---

## 💡 PART 5 — أسئلة محتملة + الإجابات

### Q: "إزاي بنغير الأرقام (Vodafone Cash، البريد)؟"
**Answer:** "من Settings → Technical → System Parameters، تلاقي 3 keys جاهزين، بتعدلهم مرة واحدة وخلاص. بدون كود، بدون deploy."

### Q: "لو العميل دفع نص المبلغ؟"
**Answer:** "النسخة الحالية بتدعم paid/unpaid فقط. الـ partial payments ممكن نضيفها كـ phase 2 لو محتاجها."

### Q: "ليه 10 أيام و6 أيام بالظبط؟"
**Answer:** "الأرقام دي configurable — لو حابب 7+5 أو 14+7 نعدّلها. بنيناها بالأرقام دي بناءً على المعايير اللي اتفقنا عليها."

### Q: "العميل المبلوك يقدر يدخل /my/orders؟"
**Answer:** "أيوه — بنبلكه من الـ shop بس، لكن بيقدر يشوف فواتيره ويدفع. لأن لو منعناه من كل حاجة هيبقى مش قادر يحل المشكلة."

### Q: "لو الفاتورة فيها 5 منتجات وعايز يلغي واحد بس؟"
**Answer:** "ده بيتم من الـ admin side، الـ Sales rep بيعدل الفاتورة. ممكن نضيف زرار "Request modification" للعميل في phase 2."

### Q: "الـ WhatsApp مرتبط بحسابكم الرسمي؟"
**Answer:** "دلوقتي بيستخدم `wa.me` — العميل بيكلم رقم محدد. لو حابب تتكامل مع WhatsApp Business API لإرسال الرسائل تلقائياً، ده integration منفصل."

---

## 🆘 PART 6 — Recovery Plan (لو حصل غلط)

| المشكلة | الحل |
|---------|------|
| الـ countdown مش ظاهر | Refresh الصفحة. لو لسه — انتقل للـ act اللي بعده وارجعله بعدين. |
| الـ confirm cart بيدي خطأ | Tab تاني، login Hany تاني، اعمل cart جديدة. |
| الـ WhatsApp مش بيفتح | اعرض الـ URL في الـ address bar — قول "بيتفتح في الموبايل". |
| الـ blocked redirect مش شغال | تأكد is_blocked=true في الـ DB، logout/login تاني. |
| Odoo بطيء | متعتذرش، استمر — بطء الـ demo environment طبيعي. |

**Emergency rollback لو الديمو فلت:**
```bash
cd "C:\Users\Sherif Taha\Desktop"
docker compose restart odoo
# انتظر 30 ثانية
```

---

## ✅ PART 7 — بعد الديمو (Closing)

**اللي تقوله في الآخر:**

> "اللي شفته دلوقتي شغال على بيئة تطوير. بعد ما توافق على الـ approach، بنحتاج منك:
> 1. أرقام Vodafone Cash والبريد و WhatsApp الحقيقية.
> 2. لوجو وألوان BlueBee لو هنخصص الـ branding.
> 3. قرار في موضوع توزيع الأرقام لو هتستخدم أكتر من محفظة Vodafone.
>
> بعد كده ننشر على Odoo SH وتبدأ تجارب فعلية."

**اطلب feedback صراحة:**
> "إيه أكتر حاجة عجبتك؟ في حاجة شايفها ناقصة؟"

---

## 📊 PART 8 — Cheat Sheet (طباعة جانبية)

```
┌─────────────────────────────────────────────────┐
│ DEMO FLOW @ A GLANCE                            │
├─────────────────────────────────────────────────┤
│ ⏱ 1m   Intro                                    │
│ ⏱ 6m   Customer Journey (Tab 1 - Hany)         │
│        └─ Add to Invoice → Cart → Portal SO    │
│        └─ Countdown (LIVE!)                     │
│        └─ Unified Invoice (merge demo)          │
│        └─ My Invoices                           │
│        └─ Pay & Close → WhatsApp                │
│ ⏱ 4m   Admin Side (Tab 2 - Mitchell)           │
│        └─ List badges                           │
│        └─ Invoice Deadline tab                  │
│        └─ Mark as Paid → unblock                │
│ ⏱ 3m   Blocked Customer (Tab 3 / Incognito)    │
│        └─ Redirect /shop → /shop/blocked        │
│        └─ Backend banner                        │
│ ⏱ 1m   Cron explanation (NO live run!)         │
│ ⏱ 5m   Q&A                                      │
├─────────────────────────────────────────────────┤
│ TOTAL: ~20 minutes                              │
└─────────────────────────────────────────────────┘
```

---

**آخر نصيحة:** متستعجلش. خد نفس بين كل act. خلي العميل يتفاعل ويسأل. الديمو الناجح مش اللي بتعرضه فيه كل feature، الديمو الناجح اللي العميل يقوم منه فاهم القيمة وعنده ثقة.

**كسرها 🚀**
