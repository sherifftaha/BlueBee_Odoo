# 🔍 Sub-Flow #2: البحث والتصفح (Search & Browse)

> **Project:** BlueBee-Eg B2B Wholesale Platform
> **Module:** `invoice_deadline` (Odoo 17)
> **Phase:** 1 — UX Planning
> **Status:** 🟡 Draft — في انتظار مراجعة شريف
> **Date:** May 2026
> **Scope:** يغطي 3 طرق وصول للمنتجات: (1) Search bar من الـ Navbar، (2) Browse عبر Category من الـ Mega Menu أو Home cards، (3) Listing page بعد filtering. كلهم بيستخدموا نفس الـ component الأساسي (Product Grid + Filters).
> **Scope note:** Covers 3 product discovery paths: (1) Search bar from Navbar, (2) Browse via Category from Mega Menu or Home cards, (3) Listing page after filtering. All share the same core component (Product Grid + Filters).

---

## 📋 جدول المحتويات | Table of Contents

1. [الهدف من الصفحة](#الهدف)
2. [النطاق والربط مع باقي الـ Flows](#النطاق)
3. [القرارات المعمارية](#القرارات-المعمارية)
4. [URL Structure](#url-structure)
5. [Sub-Flow Diagram](#sub-flow-diagram)
6. [Wireframes](#wireframes)
7. [Filter System Specification](#filter-system)
8. [Sort Options](#sort-options)
9. [Product Card Specification](#product-card)
10. [Empty States & Edge Cases](#edge-cases)
11. [Performance Targets](#performance)
12. [Inputs لـ Claude Design](#inputs-لـ-claude-design)

---

<a name="الهدف"></a>
## 🎯 الهدف من الصفحة | Page Goals

البحث والتصفح هو **القلب التجاري للموقع** — الصفحة اللي التاجر بيقضي فيها أكتر وقت. الهدف:

Search & Browse is **the commercial heart of the site** — the page where merchants spend most time. Goals:

1. **يلاقي المنتج بسرعة** — أقل من 3 كليكات من أي entry point
   Find products fast — under 3 clicks from any entry point

2. **يقيّم المنتج تجارياً** — صورة كبيرة + سعر + variants متاحة، كله من غير ما يفتح صفحة المنتج
   Evaluate commercially — large image + price + available variants, all without opening product page

3. **يقلّل decision fatigue** — فلاتر واضحة، sort افتراضي ذكي، out-of-stock مش بيضايقه
   Reduce decision fatigue — clear filters, smart default sort, out-of-stock doesn't frustrate

4. **يدعم اللغتين بدون تنازل** — RTL في عربي / LTR في إنجليزي تلقائياً
   Bilingual without compromise — RTL Arabic / LTR English automatic

---

<a name="النطاق"></a>
## 🔗 النطاق والربط مع باقي الـ Flows | Scope & Connections

هذا الـ Sub-Flow بيغطي **3 سيناريوهات بنفس الـ component:**

This Sub-Flow covers **3 scenarios with the same component:**

| السيناريو Scenario | الـ Entry Point | الـ URL |
|---|---|---|
| البحث Search | Search bar في الـ Navbar | `/shop?q=keyword` |
| تصفح القسم Category browse | Mega Menu أو Home cards | `/shop/category/<slug>` |
| تصفية Filtering | تطبيق filters على أي من فوق | `/shop?...&filters=...` |

### الربط مع Sub-Flows التانية | Connections to Other Sub-Flows

- **Sub-Flow #1 (Home):** Navbar (Search bar + Mega Menu) → دخول لهذا الـ flow
- **Sub-Flow #3 (Cart):** كل "أضف للسلة" من هذا الـ flow → يحدث الـ cart
- **صفحة المنتج (Product Page):** خارج هذا الـ flow (Sub-Flow منفصل أو inline) — لكن يتم الانتقال إليها من الـ Product Card

> **ملاحظة:** صفحة المنتج التفصيلية (Product Detail Page — PDP) **مش جزء من هذا الـ Sub-Flow**. هتتغطى في Sub-Flow منفصل لو احتجنا، أو ضمن Cart flow إذا كانت بسيطة.

---

<a name="القرارات-المعمارية"></a>
## ✅ القرارات المعمارية | Architectural Decisions

| # | القرار Decision | الاختيار Choice | السبب Rationale |
|---|---|---|---|
| 1 | الـ Scope | **Search + Browse + Filter في component واحد** | كلهم Listing pattern، توحيدهم بيقلل code duplication ويوحد الـ UX |
| 2 | Sidebar position | **inline-start** (يمين عربي / شمال إنجليزي) — CSS Logical Properties | layout بيتقلب تلقائياً مع اللغة، كود واحد للاتنين |
| 3 | Product Grid | **4 منتجات desktop / 2 mobile** | B2B best practice للـ wholesale fashion — balance بين الـ detail والـ density |
| 4 | Sort افتراضي | **الأحدث أولاً (Newest first)** | قطاع موسمي، التاجر بيدور على الجديد قبل المنافسين |
| 5 | Loading pattern | **زر "عرض المزيد" (Show More)** | يحافظ على الـ footer + scroll position، أسهل تقنياً، قابل للتغيير لاحقاً |
| 6 | Out of stock | **Clickable + Badge "نفدت" + زر "بلّغني" بدل "أضف للسلة"** | يحافظ على الـ discoverability بدون frustration |
| 7 | Stock tracking | **كل variant مخزون منفصل** (مقاس + لون = unit مستقل) | match لـ Odoo default، دقة في الـ inventory |
| 8 | Filter Sidebar | **Modular component** — يقبل فلاتر إضافية مستقبلاً بدون refactor | Phase 2 هيضيف فلاتر (Brand, New Arrivals, Best Sellers) |
| 9 | Notify back-in-stock | **إيميل في Phase 1**، WhatsApp مؤجل لـ Phase 2 | بساطة الإطلاق |
| 10 | Filter mobile UX | **Bottom sheet** (مش sidebar مطوي) | Mobile pattern معتمد عالمياً، أحسن في الـ touch |
| 11 | Search behavior | **Submit-driven** — التاجر يكتب ويدوس Enter، مفيش instant search | يقلل server load، يدي وقت للتاجر يفكر |
| 12 | URL state | **كل الفلاتر والـ sort في الـ URL** — يقدر يـ bookmark أو يشير | الـ B2B بيشارك links مع مساعدين، الـ URL لازم يكون stateful |

---

<a name="url-structure"></a>
## 🌐 URL Structure

الـ URLs بتعكس الـ filter state بالكامل (shareable + bookmarkable):

URLs reflect full filter state (shareable + bookmarkable):

### أمثلة Examples:

```
/shop                                    → كل المنتجات All products
/shop?q=بادي                              → بحث Search
/shop/category/baby                       → قسم Baby
/shop/category/baby/underwear             → subcategory
/shop?q=قميص&size=M&color=blue            → بحث + filters
/shop/category/kids?price_min=100&sort=newest
/shop?on_sale=true                        → العروض فقط
```

### Filter Query Parameters

| Parameter | المعنى | القيم |
|---|---|---|
| `q` | كلمة البحث | string |
| `category` | الفئة العمرية | `baby`, `kids`, `teens`, `women`, `men` |
| `subcategory` | تحت الفئة | depends on category |
| `size` | المقاس | `XS`, `S`, `M`, `L`, `XL`, ... |
| `color` | اللون | hex or color name |
| `price_min` / `price_max` | السعر | number |
| `gender` | الجنس | `boys`, `girls`, `unisex` (للأطفال) |
| `on_sale` | في عرض | `true` |
| `in_stock` | المتاح فقط | `true` (default behavior implicit) |
| `sort` | الترتيب | `newest`, `price_asc`, `price_desc`, `best_selling` |
| `page` | الصفحة | للـ "Show More" pagination |

> **ملاحظة Architecture:** الـ Backend (Odoo) محتاج Controller endpoint يقبل الـ query params دي ويرجع filtered products + facet counts. ده موضح في القسم الأخير "Implementation Notes for Claude Code".

---

<a name="sub-flow-diagram"></a>
## 🔀 Sub-Flow Diagram

```mermaid
flowchart TD
    Start([التاجر في الـ Home]) --> Entry{طريقة الوصول؟}

    Entry -->|كتب في Search bar + Enter| SearchURL[/shop?q=...]
    Entry -->|دوس على قسم من Mega Menu| CategoryURL[/shop/category/...]
    Entry -->|دوس على card من Home| CategoryURL

    SearchURL --> CheckResults{في نتائج؟}
    CategoryURL --> CheckResults

    CheckResults -->|آه| ListingPage[📋 Listing Page<br/>Grid + Sidebar Filters]
    CheckResults -->|لأ| EmptyState[🔍 Empty State<br/>اقتراحات]

    EmptyState -->|اقتراح من النظام| ListingPage
    EmptyState -->|عودة للهوم| Home([العودة للهوم])

    ListingPage --> UserAction{التاجر بيعمل إيه؟}

    UserAction -->|بيغيّر فلتر| ApplyFilter[تحديث الـ URL<br/>+ إعادة الـ fetch]
    UserAction -->|بيغيّر sort| ApplyFilter
    UserAction -->|دوس على منتج| ProductPage([📄 Product Page<br/>خارج الـ flow])
    UserAction -->|دوس عرض المزيد| LoadMore[تحميل صفحة جديدة]
    UserAction -->|دوس أضف للسلة من Card| AddToCart[✅ تحديث الـ Cart]
    UserAction -->|بلّغني لما يرجع| NotifyModal[📧 Modal: تأكيد إيميل]

    ApplyFilter --> CheckResults
    LoadMore --> ListingPage
    AddToCart --> ListingPage
    NotifyModal --> ListingPage

    style ListingPage fill:#012354,color:#fff
    style EmptyState fill:#94a3b8,color:#fff
    style AddToCart fill:#10b981,color:#fff
    style NotifyModal fill:#f59e0b,color:#fff
```

---

<a name="wireframes"></a>
## 🖼️ Wireframes

### 1️⃣ Listing Page — Desktop (Arabic RTL)

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🐝 BlueBee | المتجر ▾  العروض  فاتورتي | 🔍 [AR|EN] 👤أحمد 🛒(3)         │
└────────────────────────────────────────────────────────────────────────┘
│ الرئيسية > الأطفال > ملابس خروج                          24 منتج         │
│ ────────────────────────────────────────────────────────────────────── │
│                                                                        │
│  ┌──── PRODUCT GRID (3/4 width) ────┐  ┌── FILTERS (1/4 width) ──┐   │
│  │                                   │  │                          │   │
│  │  [Sort ▼ الأحدث أولاً]           │  │   🎯 الفلاتر    [مسح]    │   │
│  │                                   │  │                          │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │  │   💰 السعر               │   │
│  │  │ IMG │ │ IMG │ │ IMG │ │ IMG │ │  │   ├──○──────●──┤         │   │
│  │  │     │ │     │ │ نفدت│ │     │ │  │   100 ج    500 ج         │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ │  │                          │   │
│  │  طقم      فستان    قميص   بنطلون  │  │   📏 المقاس              │   │
│  │  255 ج    180 ج    90 ج    220 ج │  │   ☐ XS  ☐ S  ☑ M  ☑ L   │   │
│  │  [أضف]   [أضف]   [بلّغني] [أضف]  │  │   ☐ XL  ☐ 2-3y  ☐ 4-5y  │   │
│  │                                   │  │                          │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │  │   🎨 اللون                │   │
│  │  │ IMG │ │ IMG │ │ IMG │ │ IMG │ │  │   ⚪⚫🔵🔴🟢🟡🟣            │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ │  │                          │   │
│  │  ...                              │  │   👶 الفئة العمرية        │   │
│  │                                   │  │   ☐ رضع                  │   │
│  │  ┌─────────────────────────────┐ │  │   ☑ أطفال                │   │
│  │  │     عرض المزيد (16 منتج)     │ │  │   ☐ مراهقين              │   │
│  │  └─────────────────────────────┘ │  │                          │   │
│  │                                   │  │   ⚧️ الجنس                │   │
│  │                                   │  │   ☐ ولاد  ☐ بنات         │   │
│  │                                   │  │   ☑ يونيسكس              │   │
│  │                                   │  │                          │   │
│  │                                   │  │   🏷️ العروض               │   │
│  │                                   │  │   ☐ في عرض حالياً         │   │
│  │                                   │  └──────────────────────────┘   │
│  └───────────────────────────────────┘                                  │
└────────────────────────────────────────────────────────────────────────┘
```

> **ملاحظة عن الـ RTL:** في عربي، الـ Filters Sidebar **على اليمين** (بداية الـ inline)، والـ Grid على الشمال. لما يبدّل لإنجليزي، الـ layout بيتقلب تلقائياً (Sidebar شمال، Grid يمين).
>
> **RTL Note:** In Arabic, Filters Sidebar is **on the right** (inline-start), Grid on the left. Switching to English flips automatically (Sidebar left, Grid right).

---

### 2️⃣ Listing Page — Mobile (Arabic RTL)

```
┌────────────────────────┐
│ ☰  🐝 BlueBee  🔍 🛒(3) │
├────────────────────────┤
│ الأطفال > ملابس خروج    │
│ 24 منتج                │
├────────────────────────┤
│ [🎯 فلاتر] [↕ ترتيب]    │  ← Sticky bar
├────────────────────────┤
│  ┌──────┐  ┌──────┐    │
│  │ IMG  │  │ IMG  │    │
│  │      │  │ نفدت │    │
│  └──────┘  └──────┘    │
│  طقم        فستان       │
│  255 ج      180 ج       │
│  [أضف للسلة] [بلّغني]   │
│                        │
│  ┌──────┐  ┌──────┐    │
│  │ IMG  │  │ IMG  │    │
│  └──────┘  └──────┘    │
│  ...                   │
│                        │
│  ┌──────────────────┐  │
│  │  عرض المزيد       │  │
│  └──────────────────┘  │
└────────────────────────┘

(لما يدوس على "🎯 فلاتر")
        ▼
┌────────────────────────┐
│                        │
│        [content]       │
│                        │
├════════════════════════┤  ← Bottom Sheet ينزل من تحت
│ ✕  الفلاتر    [مسح]    │
│                        │
│ 💰 السعر                │
│ ├──●──────────●──┤     │
│                        │
│ 📏 المقاس               │
│ ☐ XS  ☐ S  ☑ M  ☑ L   │
│                        │
│ 🎨 اللون                │
│ ⚪⚫🔵🔴🟢🟡             │
│                        │
│ ┌──────────────────┐   │
│ │   تطبيق (8)       │   │
│ └──────────────────┘   │
└────────────────────────┘
```

**ملاحظات Mobile:**
- Filters في **Bottom Sheet** (مش sidebar) — pattern معتمد عالمياً للموبايل
- Sort في bottom sheet منفصل لما يدوس "↕ ترتيب"
- الزر **Sticky** فوق الـ grid عشان يبقى دايماً متاح
- زر "تطبيق (8)" بيعرض العدد المتوقع للنتائج قبل ما يطبق

---

### 3️⃣ Listing Page — حالة Grace (مع Banner)

```
┌────────────────────────────────────────────────────────────────────────┐
│ ⚠️ فاتورة INV-042 محتاجة دفع — 3 أيام فاضلة            [ادفع الآن]    │  ← Banner برتقالي
├────────────────────────────────────────────────────────────────────────┤
│ 🐝 BlueBee | المتجر ▾  العروض  فاتورتي(1) | 🔍 [AR|EN] 👤أحمد 🛒(3)    │
├────────────────────────────────────────────────────────────────────────┤
│ الرئيسية > الأطفال > ملابس خروج                          24 منتج         │
│                                                                        │
│            [نفس الـ listing layout]                                     │
│            Same listing layout                                         │
└────────────────────────────────────────────────────────────────────────┘
```

> الـ Banner ثابت في كل صفحات الـ Listing (نفس الـ Sub-Flow #1 pattern). التاجر يقدر يتسوّق عادي لكن التحذير ظاهر.

---

### 4️⃣ Empty State — لا توجد نتائج

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🐝 BlueBee | ...                                                       │
├────────────────────────────────────────────────────────────────────────┤
│ بحث: "بنطلون رياضي صبيان مقاس 10"                                       │
│                                                                        │
│                          🔍                                            │
│                                                                        │
│                  مفيش نتائج لبحثك                                       │
│              No results for your search                                │
│                                                                        │
│   جرّب:                                                                 │
│   • قلل عدد الكلمات                                                     │
│   • تأكد من الإملاء                                                      │
│   • شيل بعض الفلاتر [شيل كل الفلاتر]                                    │
│                                                                        │
│   ─────────────────────────                                            │
│                                                                        │
│   ممكن يعجبك:                                                          │
│   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                      │
│   │ IMG │ │ IMG │ │ IMG │ │ IMG │   ← منتجات مشابهة من نفس الفئة      │
│   └─────┘ └─────┘ └─────┘ └─────┘                                      │
│   ...                                                                  │
└────────────────────────────────────────────────────────────────────────┘
```

**سلوك الـ Empty State:**
- نص واضح بدون شعور ذنب ("مفيش نتائج" مش "ما لقيناش شيء" بحزن)
- اقتراحات عملية (قلل الكلمات، شيل فلاتر)
- زر مباشر لـ "شيل كل الفلاتر"
- منتجات مقترحة من نفس الفئة العمرية أو الـ category

---

### 5️⃣ Notify Me Modal — "بلّغني لما يرجع"

```
        ┌──────────────────────────────────────────┐
        │                                       ✕  │
        │              📧                            │
        │                                            │
        │     يرجع المنتج للمخزون قريب                │
        │     The product returns to stock soon      │
        │                                            │
        │     طقم بيتي قطن - مقاس M - أزرق           │
        │                                            │
        │     هنبعتلك إيميل لما يرجع متاح:            │
        │     We'll email you when available:        │
        │                                            │
        │   ┌──────────────────────────────────┐   │
        │   │ ahmed@example.com                 │   │ ← pre-filled
        │   └──────────────────────────────────┘   │
        │                                            │
        │   ┌────────┐    ┌──────────────────┐     │
        │   │ إلغاء  │    │   بلّغني           │     │
        │   └────────┘    └──────────────────┘     │
        └──────────────────────────────────────────┘
```

**سلوك Modal:**
- الإيميل **pre-filled** من بيانات التاجر (مش لازم يكتبه)
- يقدر يعدّله لو عاوز
- بعد التأكيد: toast notification "هنبعتلك إيميل" + Modal يقفل
- في الـ backend: record في table `product.notify.request` (product_id + variant_id + partner_id + email)

---

<a name="filter-system"></a>
## 🎯 Filter System Specification

### الفلاتر MVP (Phase 1)

| الفلتر | النوع Type | المصدر Source | ملاحظات |
|---|---|---|---|
| 💰 السعر Price | Range slider | min/max من الـ DB | dual handle |
| 📏 المقاس Size | Multi-select checkboxes | Product Attribute "Size" | بنوعين: clothing (S/M/L) أو ages (2-3y) |
| 🎨 اللون Color | Multi-select swatches | Product Attribute "Color" | بصرية مش نصية |
| 👶 الفئة العمرية Age | Multi-select | Product Category | لو دخل من mega menu بيكون pre-selected |
| ⚧️ الجنس Gender | Multi-select | Product Attribute "Gender" | ولاد / بنات / يونيسكس |
| 🏷️ العروض On Sale | Single toggle | Computed (price < regular_price) | switch بسيط |

### Modularity — التوسع المستقبلي

الـ Sidebar مبني كـ **dynamic component** يقبل array من فلاتر:

```typescript
// Pseudo-code للـ structure
filters: FilterConfig[] = [
  { id: 'price', type: 'range', label: 'السعر', ... },
  { id: 'size', type: 'multi-select', label: 'المقاس', ... },
  // Phase 2 additions:
  // { id: 'brand', type: 'multi-select', ... },
  // { id: 'new_arrivals', type: 'toggle', ... },
  // { id: 'best_sellers', type: 'toggle', ... }
]
```

**الفائدة:** إضافة فلتر جديد = صف واحد في الـ config، مفيش refactor.

### Behavior التفاعلات

| السيناريو | السلوك |
|---|---|
| التاجر دوس على فلتر | الـ URL يتحدث + الـ grid يـ fetch جديد (debounced 300ms للـ range) |
| الـ counts بجانب الفلاتر | "المقاس M (12)" — العدد بيتحدث مع كل filter change |
| فلتر متضارب بيرجع 0 نتيجة | يبان "بدون نتائج" لكن الفلتر مش بيتشال — التاجر يقرر |
| زر "مسح الفلاتر" | يرجع للحالة الافتراضية للـ URL الحالي (لو في category، يحتفظ بيها) |
| فلاتر متعددة | All filters apply with **AND** logic بين الفئات، **OR** داخل نفس الفئة |

### مثال على الـ AND/OR Logic

```
الـ User اختار:
  - المقاس: M, L (OR بينهم)
  - اللون: أزرق, أحمر (OR بينهم)
  - السعر: 100-300 ج

الـ Query:
  (size IN [M, L]) AND (color IN [blue, red]) AND (price BETWEEN 100 AND 300)
```

---

<a name="sort-options"></a>
## ↕ Sort Options

| الـ Option | الـ URL value | الـ Default؟ |
|---|---|---|
| الأحدث أولاً Newest first | `newest` | ✅ Default |
| الأكثر مبيعاً Best selling | `best_selling` | — |
| السعر: من الأرخص Price low to high | `price_asc` | — |
| السعر: من الأعلى Price high to low | `price_desc` | — |
| الاسم: أ - ي Name A-Z | `name_asc` | — |

**Behavior:**
- Dropdown في أعلى الـ Grid (يمين في عربي / شمال في إنجليزي)
- التغيير يحدث الـ URL + يـ fetch جديد فوراً
- الـ Default selection: `newest` لو مفيش `sort` في الـ URL

---

<a name="product-card"></a>
## 📦 Product Card Specification

### Anatomy تشريح البطاقة

```
┌──────────────────────────┐
│                          │
│       Product Image      │  ← aspect ratio 4:5 (B2B fashion standard)
│    (4:5 aspect ratio)    │
│                          │
│  [🏷️ -20%]    [نفدت]    │  ← badges في الكورنرز
│                          │
└──────────────────────────┘
  طقم بيتي قطن قصير          ← Product name (1 line, truncated)
  4 سنوات • قطن 100%        ← Variant hint (size + material)

  85 ج     ̶1̶0̶0̶ ̶ج̶            ← Price (with strikethrough إذا فيه discount)

  🎨 ⚪⚫🔵🔴 +3            ← Color swatches (شفها قبل ما يفتح المنتج)

  ┌──────────────────────┐
  │   + أضف للسلة         │  ← Primary action
  └──────────────────────┘
```

### Variants Display

- الـ Card بيعرض الـ **base product** (مش variant معين)
- لو فيه multiple colors → swatches بتظهر تحت السعر (max 4 + "+X" لو فيه أكتر)
- التاجر يدوس على swatch → الصورة بتتغير (preview للون قبل ما يفتح)
- زر "أضف للسلة" بيفتح الـ **Quick Add Modal** (هتتغطى في Sub-Flow #3 — Cart)

### Badges

| Badge | اللون | الشرط |
|---|---|---|
| 🆕 جديد | Navy `#012354` | المنتج اتضاف من 7 أيام |
| 🏷️ -X% | Bright Blue `#005fb2` | فيه discount |
| 🔥 الأكثر طلباً | Orange | top 10% sellers في الـ category |
| ⏳ نفدت الكمية | Gray | كل الـ variants out of stock |

### Out of Stock Variant

| الحالة | الـ Card display |
|---|---|
| كل الـ variants متاحة | Card عادي + "أضف للسلة" |
| بعض الـ variants متاحة | Card عادي + swatches للـ available فقط (الباقي disabled) |
| كل الـ variants نفدت | Card + badge "نفدت" + زر "بلّغني لما يرجع" بدل "أضف للسلة" |

---

<a name="edge-cases"></a>
## 🚨 Edge Cases & Handling

| # | Case | السلوك Behavior |
|---|---|---|
| 1 | التاجر دوس على منتج Out of stock وفتح الـ Product Page | يبان كامل، لكن زر "أضف للسلة" يتحول لـ "بلّغني" — لكن خارج هذا الـ Sub-Flow |
| 2 | الفلاتر طلعت 0 نتيجة | Empty state مع زر "مسح كل الفلاتر" مرئي وواضح |
| 3 | التاجر دخل بـ `/shop?q=xyz123` (بحث غريب) | Empty state + اقتراحات من نفس الـ category لو في، أو من الـ trending |
| 4 | التاجر دخل من Mega Menu على category فاضي تماماً | Empty state مختلف: "القسم تحت الإنشاء" + روابط لأقسام مشابهة |
| 5 | التاجر في Grace state بيتصفح | الـ Banner ظاهر، باقي الـ flow طبيعي |
| 6 | التاجر في Blocked state وفتح URL مباشر `/shop?q=...` | Redirect لشاشة البلوك (مفيش tolerance) |
| 7 | إنترنت ضعيف، الـ images بطيئة | Skeleton loaders للـ Product Cards + الـ filters بتشتغل عادي |
| 8 | التاجر دوس "عرض المزيد" والـ scroll position حافظ مكانه | بعد load، الـ scroll بيكمل من اللي توقف عنده (مش بيرجع لفوق) |
| 9 | التاجر بدّل اللغة AR↔EN وهو في listing مع filters | الفلاتر تفضل مطبقة، النصوص بس بتتترجم، الـ URL يحتفظ بكل الـ params |
| 10 | التاجر يبدّل الـ direction (AR→EN) | Sidebar بيتنقل من اليمين للشمال تلقائياً (CSS Logical Properties) |
| 11 | التاجر دوس "بلّغني" وعنده 5 منتجات نافدة | كل واحد بيتطلب confirm منفصل (مفيش bulk) — Phase 1 بساطة |
| 12 | منتج خلص من المخزون بينما التاجر بيتصفح | الـ Card مش بيتحدث live — لما يدوس على المنتج بيلاقي توست "نفد للأسف" |
| 13 | البحث بكلمة بالإنجليزي وموقع بالعربي | الـ search بيشمل الاسم بالـ 2 لغة (Odoo بيدعم translation fields) |
| 14 | الـ Range slider السعر فاضي (مفيش منتجات في النطاق) | الـ slider بيعرض الـ effective range فقط (مش 0-10000 لو الفعلي 100-500) |

---

<a name="performance"></a>
## ⚡ Performance Targets

| Metric | الهدف |
|---|---|
| First Contentful Paint (FCP) | < 1.2s on 4G |
| Time to Interactive (TTI) | < 2.5s |
| Filter apply response | < 500ms (debounced) |
| "عرض المزيد" load | < 800ms |
| Image lazy loading | كل اللي تحت الـ fold |
| Initial page size | < 200KB (HTML + critical CSS) |

### Optimization Strategies

1. **Server-side rendering للـ first page** — أول 16 منتج SSR، الباقي AJAX
2. **Image optimization** — WebP format + multiple sizes (srcset)
3. **Filter facets cached** — counts بتتحسب على intervals (مش real-time لكل request)
4. **Debounce للـ price range** — مش بيـ fetch مع كل movement
5. **Skeleton loaders** — instead of spinners

---

<a name="inputs-لـ-claude-design"></a>
## 🎨 Inputs لـ Claude Design

### الـ Bundle المطلوب

1. ✅ هذا الملف `02_search_and_browse.md`
2. ✅ `01_home.md` (Navbar reference)
3. ✅ `BUSINESS_LOGIC.md` (لمعرفة الحالات Grace/Blocked)
4. ✅ Brand Guideline PDF (Bulgia + FF Malmoom + Navy/Bright blue)

### الـ Prompts المقترحة

**Prompt 1 — Product Card Component:**
```
بناءً على design system المبني سابقاً وملف 02_search_and_browse.md:
- ابني Product Card component في React
- 4 variants: Normal, On Sale, New, Out of Stock
- aspect ratio 4:5 للصورة
- swatches للألوان (max 4 + overflow indicator)
- مزرار "أضف للسلة" أو "بلّغني" حسب الـ stock
- استخدم Brand Guideline (Navy primary, Bright Blue accent)
```

**Prompt 2 — Listing Page (Desktop + Mobile):**
```
ابني Listing Page بناءً على 02_search_and_browse.md:
- Desktop: Sidebar (inline-start) + 4-col Grid
- Mobile: Sticky filter bar + Bottom Sheet للفلاتر
- استخدم CSS Logical Properties (margin-inline-start إلخ)
- اختبر الـ AR/EN switching — الـ layout لازم يتقلب
- 3 states: Normal, Empty Results, Grace (banner)
- اختبر "عرض المزيد" interaction
```

**Prompt 3 — Filter Components:**
```
ابني الفلاتر المختلفة:
- Range slider (السعر) — dual handle
- Multi-select checkboxes (المقاس، الفئة)
- Color swatches (اللون) — visual not text
- Single toggle (العروض)
- كلهم modular — يقبلوا أي options
```

### ملاحظات حساسة لـ Claude Design

- **CSS Logical Properties إجبارية:** `margin-inline-start` بدل `margin-left`، `padding-inline-end` بدل `padding-right`، إلخ. اللغة بتتبدل بدون CSS overrides.
- **الـ Filter Sidebar مش modal** على الـ desktop — هو جزء أساسي من الـ layout
- **Bottom Sheet pattern للموبايل** — لازم يكون smooth animation، يـ dismiss بـ swipe down
- **الـ swatches للألوان لازم accessible** — aria-label للون، contrast border للألوان الفاتحة
- **Out of stock state واضح بصرياً** — Badge gray + زر مختلف، مش grayed out كله

---

## 📊 Acceptance Criteria

- [ ] الـ Listing بيلودي أقل من 3 ثواني على 4G
- [ ] الـ Filters بتتطبق مع تحديث الـ URL (shareable)
- [ ] Sort الافتراضي هو "الأحدث أولاً"
- [ ] Out of stock products بتظهر مع badge + زر "بلّغني"
- [ ] الـ Empty state بيقترح منتجات مشابهة لو فيه
- [ ] Banner الـ Grace بيظهر فوق الـ Navbar في كل صفحات الـ Listing
- [ ] التاجر في Blocked state بيتـ redirect لشاشة البلوك
- [ ] **الـ Layout بيتقلب تلقائياً مع AR↔EN (CSS Logical Properties)**
- [ ] **Mobile Bottom Sheet للفلاتر شغال بـ smooth animation**
- [ ] **الـ Grid: 4 columns desktop / 2 columns mobile**
- [ ] **زر "عرض المزيد" بيحافظ على scroll position**
- [ ] **Notify Me modal بيرسل إيميل بنجاح للـ partner**
- [ ] **الفلاتر بتشتغل مع variants (مقاس M أزرق ≠ المنتج عنده Medium بألوان تانية)**

---

## 🔗 الـ Sub-Flows المرتبطة

- **Sub-Flow #0:** Landing + Application — مش متعلق مباشرة
- **Sub-Flow #1:** Home — Navbar و Mega Menu (الـ entry points الأساسية)
- **Sub-Flow #3:** Cart & Order — كل "أضف للسلة" بيوصّل هنا (Sub-Flow التالي)
- **Sub-Flow #4:** Payment
- **Sub-Flow #5:** Post-order
- **Sub-Flow #6:** Onboarding

---

## 🛠️ Implementation Notes for Claude Code

### Backend Requirements (Odoo)

1. **Controller endpoint:** `/shop` و `/shop/category/<slug>` لازم يقبلوا query params كلها
2. **Search field on Product:** lazy translatable — الـ search بيشمل اسم بالعربي والإنجليزي
3. **Product Attributes setup:**
   - `Size` (clothing variants: XS/S/M/L/XL + age variants: 2-3y/4-5y/...)
   - `Color` (مع color hex code للـ swatches)
   - `Gender` (ولاد/بنات/يونيسكس)
4. **Notify Request Model:** new model `product.notify.request`
   - Fields: `product_id`, `product_variant_id`, `partner_id`, `email`, `notified` (boolean)
   - Cron job يومي يشيك على restock ويبعت emails
5. **Facet counts:** الـ controller يرجع counts لكل filter option (مش بس products)

### Frontend Requirements

1. **CSS Logical Properties** — `margin-inline-start`, `padding-inline-end`, إلخ
2. **`dir` attribute** على `<html>` بيتبدل مع اللغة
3. **Range slider:** استخدم library خفيفة (مش full slider lib)
4. **Bottom Sheet:** custom component أو library صغير (مش full UI lib)
5. **URL state management:** الـ filters في URL، الـ history يدعم back/forward

### Database / Migration

- مفيش schema changes كبيرة محتاجة — Odoo Product و Product Variant بيدعموا كل ده
- Migration واحد بس: إضافة model `product.notify.request`

---

## 📝 Change Log

| Date | Change | By |
|---|---|---|
| May 2026 | إنشاء أولي بناءً على قرارات شريف | Claude Chat (Opus 4.7) |

---

**🟡 Status: Draft — في انتظار مراجعة وموافقة شريف**

**🟡 Status: Draft — Awaiting Sherif's review and approval**
