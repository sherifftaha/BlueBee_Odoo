# 🎨 BlueBee — Prompts لـ Claude Design

> **طريقة الاستخدام:** ابعت كل prompt **لوحده** في شات Claude Design، وراجع المخرج قبل ما تبعت اللي بعده. مع أول prompt ارفع الـ handoff bundle كله:
> الـ 7 flows (`00`→`06`) + `BUSINESS_LOGIC.md` + `INFORMATION_ARCHITECTURE.md` + Brand Guideline (Haweity).

---

## ✅ Prompt 1 — Design System (ابدأ بده)

```
إنت بتشتغل على منصة B2B wholesale اسمها BlueBee — بيع جملة بالقطعة لملابس ومستلزمات
الأطفال والمواليد والأمهات، للتجار فقط بالدعوة، مبنية على Odoo 17. دي Phase 1.

المرفقات (اقراها كلها قبل ما تبدأ):
- INFORMATION_ARCHITECTURE.md  → هيكل الموقع وكل الصفحات والـ navigation
- BUSINESS_LOGIC.md            → قواعد العمل وحالات الفاتورة
- flows/00 → 06                → رحلات المستخدم بالتفصيل + wireframes
- Brand Guideline              → الهوية البصرية

المطلوب في الخطوة دي: ابني الـ Design System الأساسي بس (مش صفحات كاملة لسه):

1) Tokens:
   - ألوان: #012354 navy (أساسي)، #005fb2 bright blue، أبيض + ألوان دلالية لحالات الفاتورة
     (أزرق=مفتوحة، برتقالي=محتاجة دفع، أصفر=قرب الإقفال، أحمر=موقوفة، أخضر=مدفوعة)
   - خطوط: FF Malmoom للعربي / Bulgia للإنجليزي مع font-swap تلقائي حسب اللغة
   - spacing، radius، shadows

2) Components أساسية:
   button، input، product card، badge (شارات الحالة)، banner (Grace/Block)،
   navbar (بحالاته التلاتة Normal/Grace/Blocked)، mega menu، language switcher
   (pill بشكل BlueBee: AR | EN — Navy active / transparent inactive)، filter sidebar، modal.

قيود إجبارية:
- bilingual: عربي RTL افتراضي + إنجليزي LTR، باستخدام CSS Logical Properties فقط
  (مفيش CSS منفصل لكل اتجاه — الـ layout يتقلب تلقائياً مع اللغة)
- اللغة محايدة جنسياً: "اطلب / تواصل" مش "اطلبي / تواصلي"
- التزم بالهوية: navy / bright blue / أبيض + الخطين

المخرج: React + Tailwind، مع preview/showcase لكل الـ tokens والـ components.
متبنيش صفحات كاملة دلوقتي — الـ system والـ components بس. الصفحات هنعملها بعد كده واحدة واحدة.
```

---

## 🗺️ الـ Roadmap (ابعتهم واحد واحد بعد مراجعة كل واحد)

**Prompt 2 — Home (3 حالات):**
بناءً على الـ design system و `01_home.md` و `INFORMATION_ARCHITECTURE.md`: ابني الهوم `/shop` بحالاته التلاتة (Normal / Grace / Blocked)، responsive (desktop + mobile)، clickable prototype، واختبر الـ Language Switcher (AR ↔ EN).

**Prompt 3 — Listing + PDP:**
بناءً على `02_search_and_browse.md`: الـ Listing الموحّد (بحث/تصفّح/فلترة، Grid 4/2، Filters على inline-start، "عرض المزيد"، out-of-stock + "بلّغني") + صفحة المنتج (PDP — مفيش flow ليها، صمّمها من متطلبات #03: variants + أضف للسلة + تحميل الصور).

**Prompt 4 — Cart + Payment:**
بناءً على `03_cart.md` و `04_payment.md`: الكارت (mini + full + smart refresh + empty + block) → الدفع (اختيار شحن/استكمال + حسابات + نسخ + رفع سكرين + شاشة "تحت المراجعة").

**Prompt 5 — لوحة الفواتير الموحّدة + الفاتورة المفردة:**
بناءً على `05_post_order.md`: اللوحة الموحّدة `/my/invoices` بفلاترها (طلباتي النشطة / محتاجة دفع / فواتيري المنتهية) + صفحة الفاتورة المفردة (5 حالات + flag الاستكمال) + مكوّن حالة الشحن (3 مراحل) + المرتجع.

**Prompt 6 — Onboarding + الصفحات العامة:**
بناءً على `06_onboarding.md` و `00_landing_and_application.md`: Welcome + Confirm-Data gate + tour overlay، والصفحات العامة (Landing + Apply + Application Received).

---

## 🔑 تذكيرات تتكرر في كل prompt
- bilingual إجباري بـ CSS Logical Properties
- الهوية: navy `#012354` / bright blue `#005fb2` / أبيض + FF Malmoom / Bulgia
- لغة محايدة جنسياً
- لغة التاجر مش لغة المطوّر في كل النصوص الظاهرة (مثلاً "محتاجة دفع" مش "Locked")
- الكمية الدقيقة للمخزون متظهرش أبداً ("الكمية المتوفرة أقل" بدون أرقام)
