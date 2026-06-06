# 🗺️ BlueBee Information Architecture
## هيكل المعلومات لموقع BlueBee | BlueBee Site Information Architecture

**آخر تحديث | Last updated:** 2026-06-06
**الحالة | Status:** Phase 1 — **v3: متوافق مع الملفات السبعة + قرار اللوحة الموحّدة** (طلباتي/فواتيري = view-ين مفلترين من لوحة واحدة). جزء من الـ handoff bundle لـ Claude Design | **v3: aligned with the 7 flow files + unified-dashboard decision** (Orders/Invoices = two filtered views of one dashboard). Part of the Claude Design handoff bundle.
**المرجع | Reference:** العمود الفقري الهيكلي — جرد كل الصفحات، الـ navigation، والـ taxonomy. بيكمّل الـ flows (الرحلات) والـ `BUSINESS_LOGIC.md` (القواعد) | Structural backbone — inventory of pages, navigation, taxonomy. Complements the flows and `BUSINESS_LOGIC.md`.

---

## 🎯 الهدف من الملف | Purpose

الـ flows بتوصف **الرحلات**. الملف ده بيوصف **الهيكل الثابت**: إيه الصفحات الموجودة، إزاي متجمّعة، وشكل الـ navigation.
The flows describe **journeys**. This file describes the **static structure**: what pages exist, how they're grouped, and the navigation shape.

---

## 📑 المحتويات | Table of Contents

1. [خريطة الموقع (Sitemap)](#1-خريطة-الموقع--sitemap)
2. [جرد الصفحات (Page Inventory)](#2-جرد-الصفحات--page-inventory)
3. [تصنيف المنتجات (Taxonomy)](#3-تصنيف-المنتجات--product-taxonomy)
4. [الـ Navigation العام](#4-الـ-navigation-العام--global-navigation)
5. [خريطة الـ URLs](#5-خريطة-الـ-urls--url-map)
6. [طلباتي vs فواتيري](#6-طلباتي-vs-فواتيري--orders-vs-invoices)
7. [الربط بين الصفحات](#7-الربط-بين-الصفحات--cross-flow-connections)
8. [الـ Overlays والحالات](#8-الـ-overlays-والحالات--overlays--non-page-states)
9. [ملاحظات وقرارات لـ Claude Design](#9-ملاحظات-وقرارات-لـ-claude-design--notes--decisions)

---

## 1. خريطة الموقع | Sitemap

```
BlueBee Site
│
├── 🌐 منطقة عامة | Public Zone (غير مسجّل | unauthenticated)
│   ├── Landing Page                 /                       (تاجر مسجّل → redirect لـ /shop)
│   ├── Application Form             /apply
│   ├── Application Received         /application-received
│   ├── Login                       /web/login
│   └── Signup / Set Password       /web/signup              (من لينك الدعوة)
│
└── 🔐 منطقة التاجر | Merchant Zone (مسجّل + active | authenticated)
    │
    ├── Home                        /shop                    (منسّق: hero + كروت + عروض)
    │   ├── Hero / New Arrivals carousel
    │   ├── Shop by Age cards (×5)
    │   ├── Promotions
    │   └── Footer
    │
    ├── 🎓 Onboarding (أول login | first login)
    │   ├── Welcome                  /shop/welcome
    │   ├── Confirm Data (gate)      /shop/confirm-data
    │   └── (الجولة = overlay فوق /shop | tour = overlay)
    │
    ├── 🛍️ التسوّق | Shopping
    │   ├── Listing (Search/Browse/Filter)  /shop/category/<slug>  •  /shop?q=  •  /shop?<filters>
    │   ├── Offers (listing مفلتر)           /shop?on_sale=true
    │   ├── Product Detail Page (PDP) ⚠️     /shop/<product>        (محتاج تصميم — مفيش flow)
    │   └── Cart                            /shop/cart
    │
    ├── 📄 الفواتير (لوحة موحّدة) | Invoices (unified dashboard)
    │   ├── Dashboard                /my/invoices             (الكل | All — default = طلباتي النشطة)
    │   │   ├── طلباتي My Orders     /my/invoices?state=active   (open/locked/grace/blocked + استكمال)
    │   │   ├── محتاجة دفع Payment   /my/invoices?state=payment  (locked + grace)
    │   │   └── فواتيري Finished     /my/invoices?state=paid     (paid، مش استكمال)
    │   ├── Single Invoice           /my/invoices/<id>
    │   └── Payment                  /my/invoices/<id>/pay  →  /pay/shipping · /pay/continue · /pay/review
    │
    ├── 🔄 المرتجع | Returns
    │   └── Returns / Defects        /my/returns              (سياسة + واتساب)
    │
    └── ⚙️ الحساب | Account
        ├── Settings / Profile       /my/account
        └── Logout                   /web/session/logout
```

> 🚫 **حالة البلوك | Blocked state:** لما `is_blocked = True`، التاجر بيشوف **شاشة بلوك كاملة** فوق أي route، بـ navbar مبسّط (الاسم + Language Switcher + logout) + زر تواصل خدمة العملاء. مش صفحة منفصلة — حالة بتتفرض.
> 🚫 **Blocked state:** When `is_blocked = True`, the merchant sees a **full block screen** over any route, with a minimal navbar (name + Language Switcher + logout) + customer service button. Not a separate page — an imposed state.

---

## 2. جرد الصفحات | Page Inventory

| # | الصفحة Page | الـ URL | الوصول Access | الغرض Purpose | المصدر Flow |
|---|---|---|---|---|---|
| 1 | Landing Page | `/` | عام Public | جذب التجار الجدد + SEO | #00 |
| 2 | Application Form | `/apply` | عام Public | استقبال طلب الانضمام (8 حقول) | #00 |
| 3 | Application Received | `/application-received` | عام Public | تأكيد الاستلام + لينكات تليجرام | #00 |
| 4 | Login | `/web/login` | عام Public | دخول التاجر (active فقط) | #00 |
| 5 | Signup / Set Password | `/web/signup` | عام (بلينك) | قبول الدعوة + عمل باسورد → active | #00 |
| 6 | Home | `/shop` | تاجر Merchant | البوابة الرئيسية، 3 حالات (Normal/Grace/Blocked) | #01 |
| 7 | Onboarding — Welcome | `/shop/welcome` | تاجر Merchant | شاشة ترحيب أول login | #06 |
| 8 | Onboarding — Confirm Data | `/shop/confirm-data` | تاجر Merchant | gate تأكيد البيانات قبل أول checkout | #06 |
| 9 | Listing (Search/Browse/Filter) | `/shop/category/<slug>` · `/shop?q=` · `/shop?<filters>` | تاجر Merchant | شبكة المنتجات الموحّدة | #02 |
| 10 | Offers | `/shop?on_sale=true` | تاجر Merchant | listing مفلتر على العروض | #01/#02 |
| 11 | Product Detail Page ⚠️ | `/shop/<product>` | تاجر Merchant | تفاصيل + variant + أضف للسلة + تحميل صور — **محتاج تصميم، مفيش flow** | gap |
| 12 | Cart | `/shop/cart` | تاجر Merchant | السلة (mini + full) + التأكيد | #03 |
| 13 | Invoices Dashboard (موحّد) | `/my/invoices` | تاجر Merchant | لوحة موحّدة لكل الفواتير + فلاتر (طلباتي / محتاجة دفع / فواتيري) | #05 |
| 14 | Single Invoice | `/my/invoices/<id>` | تاجر Merchant | تفاصيل + أكشن + سبب رفض + حالة شحن + تحميل صور + بلّغ عن ديفو | #04/#05 |
| 15 | Payment | `/my/invoices/<id>/pay/...` | تاجر Merchant | شحن/استكمال + حسابات + رفع سكرين + شاشة مراجعة | #04 |
| 16 | Returns / Defects | `/my/returns` | تاجر Merchant | عرض سياسة المرتجع + زر واتساب | #05 |
| 17 | Account / Settings | `/my/account` | تاجر Merchant | بيانات التاجر + العنوان + اللغة | Odoo portal |

---

## 3. تصنيف المنتجات | Product Taxonomy

التصنيف **age-first** (حسب العمر الأول) — قرار Sub-Flow #01. منقول بالكامل من `01_home.md`:
Age-first taxonomy — decision from Sub-Flow #01. Copied in full from `01_home.md`:

```
المنتجات | Products
│
├── 👶 الرضع | Baby (0–24 شهر | months)
│   ├── ملابس خروج  | Outerwear
│   ├── ملابس بيت   | Loungewear
│   ├── Underwear
│   ├── أحذية       | Footwear
│   └── مستلزمات    | Essentials
│
├── 🧒 الأطفال | Kids (2–12 سنة | years)
│   ├── ملابس خروج
│   ├── ملابس بيت
│   ├── Underwear
│   ├── أحذية
│   ├── شنط         | Bags
│   └── 🎒 إكسسوارات | Accessories (parent)
│       ├── ملابس بحر | Swimwear
│       ├── كوستيومز  | Costumes
│       └── إسدالات   | Abayas
│
├── 🧑 المراهقين | Teens (12–18 سنة | years)
│   ├── ملابس خروج
│   ├── ملابس بيت
│   ├── Underwear
│   ├── أحذية
│   ├── شنط
│   └── 🎒 إكسسوارات | Accessories (نفس الـ subs)
│
├── 👩 السيدات | Women
│   ├── ملابس حوامل | Maternity
│   ├── ملابس بيت   | Home wear
│   └── كاجوال      | Casual
│
└── 👨 الرجال | Men
    ├── ملابس بيت
    └── كاجوال
```

قسم عرضي مش عمري | Cross-cutting non-age section:
```
└── 🏷️ العروض | Promotions  →  /shop?on_sale=true
```

- التصنيف ده بيظهر في الـ Mega Menu + كروت "تسوّق حسب الفئة" في الهوم | Drives the Mega Menu + "Shop by Age" home cards
- الـ slugs: `baby` · `kids` · `teens` · `women` · `men` (+ subcategory slugs) | Category slugs as listed

---

## 4. الـ Navigation العام | Global Navigation

### 🖥️ Navbar — Desktop (Normal / Grace state)

ترتيب RTL (من اليمين للشمال) — يتقلب تلقائياً بـ CSS Logical Properties:
RTL order (right→left) — flips automatically via CSS Logical Properties:

| العنصر Element | الوظيفة Function |
|---|---|
| 🐝 Logo | يرجّع للهوم `/shop` | Returns to Home |
| المتجر ▾ Mega Menu | الفئات العمرية الـ 5 + sub-categories | 5 age categories + subs |
| العروض Offers | `/shop?on_sale=true` |
| 📦 طلباتي My Orders | `/my/invoices?state=active` — **badge** في Grace/Blocked (طلب محتاج دفع) | badge in Grace/Blocked |
| 🔍 Search | يفتح search overlay → `/shop?q=` |
| 🌐 Language Switcher | pill: AR \| EN (Navy active / transparent inactive)، cookie | persisted in cookie |
| 👤 Account dropdown | الاسم → بياناتي · طلباتي (`?state=active`) · فواتيري (`?state=paid`) · تسجيل خروج | name → profile · orders · invoices · logout |
| 🛒 Cart | عدد القطع | piece count |

> 💡 **طلباتي و فواتيري مدخلان لنفس اللوحة** (`/my/invoices`) بفلتر مختلف، مش لوحتين منفصلتين. | Orders and Invoices are two filtered entries to the **same** dashboard, not two separate pages.

### الـ Navbar حسب حالة التاجر | Navbar by state

| الحالة State | الشكل Appearance |
|---|---|
| 🟦 Normal / Continuation | Navbar كامل، مفيش بانر | Full navbar, no banner |
| 🟨 Grace (يوم 11–16) | Navbar كامل + **بانر برتقالي** ثابت (رقم الطلب + الأيام المتبقية + زر دفع) + badge على طلباتي | Full + orange banner + badge on Orders |
| 🟥 Blocked (يوم 17+) | **Navbar مبسّط** (اسم + Language Switcher + logout) + شاشة بلوك كاملة | Minimal navbar + full block screen |

### 📱 Navbar — Mobile

```
┌────────────────────────┐
│ ☰   🐝 BlueBee   🔍 🛒(3)│   ← Hamburger يفتح القائمة الكاملة
└────────────────────────┘
        │ (tap ☰)
        ▼
   أهلاً [اسم التاجر]  ·  📦 طلباتي
   ─────────────────────────────
   🏠 الرئيسية
   👶 الرضع        ▸  (list فرعية)
   🧒 الأطفال       ▸
   🧑 المراهقين      ▸
   👩 السيدات       ▸
   👨 الرجال        ▸
   🏷️ العروض
   ─────────────────────────────
   📄 فواتيري · ⚙️ الإعدادات · 🚪 تسجيل خروج
```

### 🦶 Footer

سياسة الشركة · أرقام التواصل (استلامات / عملاء جدد / شكاوى) · لينكات قنوات تليجرام · العنوان (المنصورة — حي الجامعة، شارع الحنتيري) · Language switcher (نسخة footer اختيارية).
Company policy · contact numbers · Telegram channel links · address · optional footer language switcher.

---

## 5. خريطة الـ URLs | URL Map

| الـ Route | الصفحة Page | الوصول Access |
|---|---|---|
| `/` | Landing (غير مسجّل) / redirect لـ `/shop` (مسجّل) | عام / تاجر |
| `/apply` | Application Form | عام |
| `/application-received` | Application Received | عام |
| `/web/login` | Login | عام |
| `/web/signup` | Signup / Set Password | عام (بلينك) |
| `/shop` | Home (منسّق) | تاجر |
| `/shop/welcome` | Onboarding Welcome | تاجر |
| `/shop/confirm-data` | Onboarding Confirm Data (gate) | تاجر |
| `/shop/category/<slug>` | Listing — تصفّح فئة | تاجر |
| `/shop/category/<slug>/<sub>` | Listing — تصنيف فرعي | تاجر |
| `/shop?q=<keyword>` | Listing — نتيجة بحث | تاجر |
| `/shop?<filters>&sort=` | Listing — مفلتر (الفلاتر في الـ URL) | تاجر |
| `/shop?on_sale=true` | Offers | تاجر |
| `/shop/<product>` | Product Detail Page ⚠️ | تاجر |
| `/shop/cart` | Cart | تاجر |
| `/my/invoices` | Invoices Dashboard (موحّد، الكل) | تاجر |
| `/my/invoices?state=active` | طلباتي — النشطة (open/locked/grace/blocked + استكمال) | تاجر |
| `/my/invoices?state=payment` | محتاجة دفع (locked + grace) | تاجر |
| `/my/invoices?state=paid` | فواتيري — المنتهية (paid، مش استكمال) | تاجر |
| `/my/invoices/<id>` | Single Invoice | تاجر |
| `/my/invoices/<id>/pay` | اختيار المسار + الدفع | تاجر |
| `/my/invoices/<id>/pay/shipping` | مسار الشحن | تاجر |
| `/my/invoices/<id>/pay/continue` | مسار الاستكمال | تاجر |
| `/my/invoices/<id>/pay/review` | تحت المراجعة | تاجر |
| `/my/returns` | Returns / Defects | تاجر |
| `/my/account` | Account / Settings | تاجر |
| `/web/session/logout` | Logout | تاجر |

> 🔗 **الفلاتر والـ sort والبحث كلهم في الـ URL** (shareable) — التاجر بيشارك links مع موظفيه. قرار Sub-Flow #02 و#05.
> 🔗 Filters, sort, and search all live in the URL (shareable). Decision from Sub-Flows #02 & #05.

---

## 6. طلباتي vs فواتيري | Orders vs Invoices

**لوحة واحدة موحّدة** (`/my/invoices`) بتعرض كل الفواتير، و"طلباتي" و"فواتيري" **مجرّد view-ين مفلترين** منها (قرار #05 رقم 1: اللوحة الموحّدة + تقسيمة التاجر بالحالة). الفلتر مبني على `invoice_state` (`BUSINESS_LOGIC.md` §2):
**One unified dashboard** (`/my/invoices`) shows all invoices; "Orders" and "Invoices" are just **two filtered views** of it (Decision #1 in #05: unified dashboard + merchant's state grouping). Filtering is based on `invoice_state` (`BUSINESS_LOGIC.md` §2):

| الفلتر View | الـ URL | الحالات المعروضة States shown |
|---|---|---|
| 📦 **طلباتي My Orders** (default) | `/my/invoices?state=active` | `open` · `locked` · `grace` · `blocked` + الاستكمال (`is_continuation = True` على `open`) | All active |
| 💳 محتاجة دفع Needs payment | `/my/invoices?state=payment` | `locked` + `grace` | Urgent subset |
| 📄 **فواتيري Finished** | `/my/invoices?state=paid` | `paid` فقط (ومش استكمال) — المكتمل | Paid & final only |
| الكل All | `/my/invoices` | الكل | Everything |

- الطلب بيظهر في **طلباتي** طول ما هو نشط، والدفع بيتم من صفحته (`/my/invoices/<id>/pay`) | An order appears under **Orders** while active; payment happens on its page
- بعد تأكيد الدفع النهائي (`paid`) → يظهر في **فواتيري** | After final payment confirmation (`paid`) → appears under **Invoices**
- الاستكمال بيفضل في **طلباتي** لأن الطلب لسه مفتوح للإضافة رغم إن في دفعة اتعملت | Continuation stays under **Orders** since it's still open for additions despite a payment

---

## 7. الربط بين الصفحات | Cross-Flow Connections

```
Telegram link ──┐
Direct URL    ──┴──> [Auth check]
                       │
            مش مسجّل   │   مسجّل + active
            ┌──────────┴──────────┐
            ▼                     ▼
        Landing (/)        أول login? ── آه ──> /shop/welcome ─> /shop/confirm-data
            │                     │ لأ                              │
        /apply               /shop (Home) <───────────────────────┘
            │              ┌──────┼───────┬─────────────┐
       /application-     Mega   Search   Home cards    Account ▾
        received         Menu     │         │          ┌────┴────┐
                          └───────┼─────────┘      طلباتي     فواتيري
                                  ▼              (?state=active) (?state=paid)
                          Listing (/shop/...)        └────┬────┘
                                  │                       ▼
                                  ▼              /my/invoices (لوحة موحّدة)
                         Product (PDP) ⚠️                 │
                                  │                /my/invoices/<id>
                                  ▼              ┌────────┼────────┐
                              Cart (/shop/cart)  ▼        ▼        ▼
                                  │           /pay/...  حالة شحن  /my/returns
                          Confirm ── (data gate لو أول مرة) ──> /shop/confirm-data
                                  │
                                  ▼
                          order created → /my/invoices/<id>
```

- **دخول بلينك منتج من تليجرام:** لو مش مسجّل → `/web/login` (مع حفظ لينك المنتج) → بعد الدخول يروح للمنتج | Telegram product link: if not logged in → login (saving link) → then product
- **إضافة للسلة + طلب مفتوح موجود:** بيدمج حسب أولوية الفاتورة (`BUSINESS_LOGIC.md` §7) | Add to cart with existing open order: merges per priority
- **gate تأكيد البيانات:** بيشتغل عند أول checkout فقط، مرة واحدة | Data-confirm gate: fires only at first checkout, once

---

## 8. الـ Overlays والحالات | Overlays & Non-Page States

مش صفحات — عناصر بتظهر فوق الصفحات أو حالات بتتفرض:
Not pages — elements layered over pages or imposed states:

| العنصر Element | الطبيعة Nature | المصدر Flow |
|---|---|---|
| Onboarding tour | **Overlay skippable** فوق `/shop` (متحكّم فيه `onboarding_completed`) | #06 |
| Block screen | شاشة كاملة بتتفرض لما `is_blocked = True` | #01/#08 |
| Mini cart | Dropdown/drawer من أيقونة السلة (مش URL) | #03 |
| Surcharge modal | يظهر لو أقل من 6 قطع وقت الشحن | #04 |
| Restock notify modal | تأكيد إيميل لطلب إشعار التوفّر | #02 / BL §10 |
| Grace banner | بانر برتقالي ثابت في حالة Grace | #01 |
| Smart cart refresh | تنبيه للـ variants اللي خلصت تماماً (out-of-stock = 0) فقط | #03 |
| Confirm result | بعد الـ Confirm: redirect لـ `/my/invoices/<id>` أو modal بالمنتجات الناقصة (مفيش صفحة Confirm منفصلة) | #03 |

> ✅ **Onboarding:** التاجر يتصفّح ويضيف للسلة بحرية. الـ gate الوحيد عند **Checkout** ويتعدّى **مرة واحدة**. شاشتا Welcome + Confirm-Data ليهم routes، الجولة overlay.
> ✅ **Onboarding:** Browse and add to cart freely. The only gate is at **Checkout**, passed **once**. Welcome + Confirm-Data are routed pages; the tour is an overlay.

---

## 9. ملاحظات وقرارات لـ Claude Design | Notes & Decisions

### قرارات توحيد الـ routes (v3) | Route reconciliation decisions
1. **الهوم = `/shop`** (الـ approved في #01). شبكة المنتجات تظهر مع category/بحث/فلاتر فقط — مفيش "bare /shop = كل المنتجات". | Home = `/shop`; product grid only with category/search/filters.
2. **لوحة فواتير موحّدة واحدة `/my/invoices`** (قرار #05). طلباتي = `?state=active`، فواتيري = `?state=paid` — view-ين مفلترين مش لوحتين. صفحة الطلب `/my/invoices/<id>` والدفع `/my/invoices/<id>/pay/...`. اتشال `/shop/invoice/<id>` بتاع #04. | Unified `/my/invoices`; Orders/Invoices are filtered views; dropped `/shop/invoice/<id>`.
3. **Login = `/web/login`** (وحّدنا الخلاف بين #00 و#01). | Unified login route.

### gap محتاج انتباه | Gap to flag
4. ⚠️ **صفحة المنتج (PDP) مالهاش flow مخصص.** route طبيعي `/shop/<product>`. متطلباتها المعروفة من #03: عرض variants (مقاس+لون)، أضف للسلة، تحميل الصور (ZIP/PDF). Claude Design يصممها من دول + Odoo default. | PDP has no dedicated flow; design from #03 requirements + Odoo default.

### مبادئ تصميم | Design principles
5. **bilingual إجباري:** كل شاشة RTL (عربي default) و LTR (إنجليزي) بـ CSS Logical Properties فقط. | Mandatory bilingual via logical properties.
6. **الهوية:** `#012354` navy + `#005fb2` bright blue + أبيض، خطوط FF Malmoom (AR) / Bulgia (EN). | Brand identity.
7. **لغة محايدة جنسياً:** "اطلب / تواصل". | Gender-neutral copy.
8. **3 حالات للهوم/الـ navbar:** Normal / Grace / Blocked. | 3 states.
9. **Component موحّد للـ Listing:** بحث + تصفّح + فلترة نفس الـ component (Filters على inline-start). | Unified Listing component.
10. **رسمة مقترحة للـ bundle:** Merchant Account State Machine (pending → approved → active / rejected). | Suggested diagram for the bundle.

---

## 🔗 الملفات المرتبطة | Related Files

- `BUSINESS_LOGIC.md` — قواعد العمل | Business rules
- `flows/00_landing_and_application.md` … `flows/06_onboarding.md` — الرحلات | Journeys
- Brand Guideline 2024 (Haweity Design House)

---

**End of document | نهاية الملف**
