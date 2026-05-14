# BlueBee_Odoo — Invoice Deadline & Blocking Module
## نظام مواعيد الفواتير والحجب — BlueBee-Eg

> **For AI assistants (Claude, Copilot, Cursor, etc.):**
> This file is your single source of truth for understanding this project.
> Read it fully before making any suggestions or changes.

---

## Project Overview — نظرة عامة

**Company:** BlueBee-Eg — ملابس أطفال ومستلزمات بالجملة بالقطعة  
**Location:** المنصورة، مصر  
**Platform:** Odoo 17.0 (Educational/Demo instance on Docker)  
**Production:** Odoo SH  
**Business Model:** B2B only — wholesale to registered merchants (invitation only)

**Module name:** `invoice_deadline`  
**Purpose:** Enforces a 10-day invoice payment window. Customers who don't pay get blocked from placing new orders. Includes a grace period, cascade blocking, and automatic unblocking on payment.

---

## Environment — البيئة

| Item | Value |
|------|-------|
| Odoo Version | 17.0 |
| Platform | Docker on Windows 10 |
| docker-compose.yml | `C:\Users\Sherif Taha\Desktop\docker-compose.yml` |
| Custom module path | `C:\odoo-modules\invoice_deadline\` |
| DB container | `desktop-db-1` |
| Odoo container | `desktop-odoo-1` |
| Database name | `odoo` |
| Odoo URL | `http://localhost:8069` |

### Key Docker Commands

```bash
# Restart Odoo
cd "C:\Users\Sherif Taha\Desktop"
docker compose restart odoo

# Upgrade module after code changes
docker compose exec odoo odoo -u invoice_deadline -d odoo --db_host=db --db_user=odoo --db_password=odoo --stop-after-init

# Run SQL
docker compose exec db psql -U odoo -d odoo -c "YOUR SQL HERE"
```

---

## Business Rules — قواعد العمل

### Sales Rules
- B2B only — wholesale merchants, no retail
- Minimum order: **6 pieces**
- Orders under 6 pieces: **+25 EGP per piece** surcharge
- Invitation-only website registration

### Loyalty / Discount System
| Level | Arabic | Discount | Threshold |
|-------|--------|----------|-----------|
| Bronze | برونزي | 5% | From first piece |
| Silver | فضي | 10% | After 5,000 EGP cumulative spend |
| Gold | ذهبي | 15% | After 15,000 EGP cumulative spend |

---

## Invoice Lifecycle — دورة حياة الفاتورة

```
Day 0:   Customer confirms order from website cart
         → Sale Order (SO) created
         → invoice_open_date = today
         → invoice_state = 'open'

Day 0-10: Open period
         → Customer can add more products to the same SO
         → If customer confirms again → lines merged into existing SO (no new SO)

Day 11:  Cron job runs
         → invoice_state: open → locked
         → Warning shown to customer on website

Day 11-16: Grace period
         → Customer can open a new SO (#2) with its own counter
         → SO #1 is locked, awaiting payment

Day 17:  Cron job runs
         → If SO #1 still unpaid:
         → invoice_state: locked/grace → blocked
         → partner.is_blocked = True
         → ALL other SOs for this partner also blocked (cascade)

Payment:
         → invoice_state = 'paid'
         → partner.is_blocked = False
         → Other SOs resume their timers (open question — see below)
```

---

## File Structure — هيكل الملفات

```
invoice_deadline/
├── __manifest__.py          # Module metadata & dependencies
├── __init__.py              # Imports: models, controllers
├── models/
│   ├── __init__.py
│   ├── res_partner.py       # Adds is_blocked field to customer
│   ├── sale_order.py        # Core logic: lifecycle, cron, confirm, unified SO, mark paid
│   ├── account_move.py      # Auto-detects payment → unblocks partner
│   └── website.py           # Website-related overrides
├── controllers/
│   ├── __init__.py
│   └── main.py              # Website cart/checkout overrides (block + merge redirect)
├── views/
│   ├── sale_order_views.xml  # Backend: Invoice tab, status badge, list column
│   ├── res_partner_views.xml # Backend: Block banner + toggle button
│   └── templates.xml         # Website: cart alerts, countdown timer, checkout block
├── static/src/js/
│   ├── invoice_deadline.js   # Countdown timer (Odoo 17 module format)
│   └── cart_modal_patch.js   # Cart modal OWL component patch
└── data/
    ├── cron.xml              # Daily cron job definition
    ├── payment_config.xml    # Payment configuration data
    └── below_minimum_fee_product.xml  # Service product for +25 EGP surcharge
```

---

## Database Fields — حقول الداتابيز

### On `sale.order`
| Field | Type | Description |
|-------|------|-------------|
| `invoice_open_date` | Datetime | When order was confirmed (Day 0) |
| `invoice_deadline_date` | Datetime | Locking date (open_date + 10 days) — computed |
| `grace_end_date` | Datetime | Blocking date (open_date + 16 days) — computed |
| `invoice_state` | Selection | `open` / `locked` / `grace` / `blocked` / `paid` |
| `merged_into_so_id` | Many2one | Points to the SO this one was merged into |

### On `res.partner`
| Field | Type | Description |
|-------|------|-------------|
| `is_blocked` | Boolean | Customer is blocked due to unpaid invoices |

---

## Core Logic — المنطق الأساسي

### Unified Invoice (SO Merging)
When a customer confirms a new cart while they already have an open/locked SO:
- The new SO's lines are **moved** into the existing SO
- The new SO is **deleted**
- The customer is **redirected** to the existing SO
- The invoice timer does **not** reset

### Cron Job (`_cron_update_invoice_states`)
Runs daily. Two passes:
1. `open` → `locked` (when `invoice_deadline_date` has passed)
2. `locked`/`grace` → `blocked` (when `grace_end_date` has passed) + cascade to all partner SOs + set `is_blocked = True`

### Payment Detection
- **Auto:** `account.move` write override detects payment state change → marks SO as paid, unblocks partner
- **Manual:** "Mark as Paid" button on SO form

### Website Blocking
- Blocked customers cannot proceed to checkout
- Cart shows alert banner (info/warning/danger) based on `invoice_state`
- Countdown timer shows days remaining

---

## What's Done ✅

- [x] Invoice deadline fields on `sale.order`
- [x] `is_blocked` field on `res.partner`
- [x] Daily cron: open → locked → blocked (with cascade)
- [x] Block confirmation for blocked customers
- [x] Unified Invoice — merge cart into existing SO
- [x] Payment closes invoice (auto via `account.move` + manual button)
- [x] Backend UI — tab on SO form, status badge, list column, partner banner
- [x] Website UI — alerts, countdown, checkout block
- [x] Minimum 6-piece rule with +25 EGP/piece surcharge

## What's Pending ⏳

- [ ] Website countdown timer JS (Odoo 17 module format — DOMContentLoaded issue)
- [ ] Payment auto-detection testing with full Create Invoice flow
- [ ] Website checkout block testing with a blocked user account
- [ ] Clean up cancelled test records in DB
- [ ] Multi-payment wallet (Vodafone Cash) — sticky round-robin distribution

---

## Open Questions — أسئلة مفتوحة

1. **After unblocking:** When SO #1 is paid and partner is unblocked, SO #2 (blocked mid-timer) — does it resume from where it stopped, restart from Day 0, or get cancelled? *Needs owner decision.*

2. **Delivery/service products:** Should delivery fees count toward the 6-piece minimum? *Deferred — no service products in use yet.*

3. **Draft quotations:** Should a new cart merge into a draft (unconfirmed) SO, or only into confirmed SOs?

---

## Important Technical Notes — ملاحظات تقنية

1. **Computed fields** (`invoice_deadline_date`, `grace_end_date`) don't recalculate if you update `invoice_open_date` directly via SQL. Use Odoo shell or update both fields manually.

2. **`is_blocked` default:** Doesn't apply to old records. Run:
   ```sql
   UPDATE res_partner SET is_blocked = false WHERE is_blocked IS NULL;
   ```

3. **Database name is `odoo`**, not `postgres`.

4. **After any code change:** Upgrade module + restart Odoo (see Docker commands above).

5. **Missing license warning** in logs is normal — not an error.

---

## Developer — المطور

**Sherif Taha** — `taaskm@gmail.com`  
Project: BlueBee-Eg Odoo B2B E-commerce  
Last updated: 2026-05-15
