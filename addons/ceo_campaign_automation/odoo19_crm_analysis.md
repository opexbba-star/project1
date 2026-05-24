# Odoo 19 Enterprise — CRM Automation Solution: Architecture Analysis

> **Scope:** Odoo 19 Enterprise Edition | **Analyst Role:** Solution Architect / Functional-Technical Analyst  
> **Date:** May 2026 | **Basis:** Odoo 19 official documentation + research on released features

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Fully available natively |
| 🟡 | Partially available / requires configuration |
| ❌ | Not available natively — requires custom development |
| ⭐ | Enterprise Edition only |

---

## PART 1 — Contacts Database Upload & Smart Mapping

| # | Feature / Requirement | Available Natively? | Existing Odoo Module(s) | Native Functionality | AI Features in Odoo 19 | Required Customization | Recommended Approach | Complexity | Notes / Risks |
|---|---|---|---|---|---|---|---|---|---|
| 1.1 | Upload CSV / Excel file to `res.partner` | ✅ Native | `base_import` (Import Contacts wizard) | Supports CSV + XLSX import. Auto-detects delimiters. Handles 2MB files by default. | None | None for basic use | Use native import as base; extend for advanced preprocessing | Low | Native limit: ~50,000 rows per session depending on server config |
| 1.2 | Automatic column-to-field mapping (heuristic) | 🟡 Partial | `base_import` | Matches headers to field names heuristically. Supports manual override from dropdown. Does NOT do semantic/AI matching. | None native | Custom import wizard with heuristic + AI-based mapping engine  | Extend native wizard OR build standalone wizard | Medium | Native matching is exact/near-exact label matching only |
| 1.3 | Mapping to existing `res.partner` field | ✅ Native | `base_import` | All declared fields in `res.partner` are selectable including custom `x_` fields | None | None | Use native dropdown | Low | Fields must exist before import |
| 1.4 | Dynamic new field creation during import (user-prompted) | ❌ Not Native | `base_import` / `ir.model.fields` | No native capability. Fields must exist before import. | None | Full custom wizard: user reviews unmapped columns → chooses label/description → system creates `x_new_field_*` via `ir.model.fields` API + updates view | New module: `ceo_campaign_automation` ✅ (already started implementation) | High | Risk: requires `ir.model.fields` write access + registry reload. Odoo 19 registry reload via `setup_models()` is stable. |
| 1.5 | Semantic / AI-based column mapping (analyze content) | ❌ Not Native | None | Not available natively | None (Odoo AI does not cover import column analysis) | Custom: regex heuristics (email, phone, URL patterns) + Gemini API fallback | New module: `ceo_campaign_automation` ✅ (already considered implementation) | High | Cost: Gemini API calls per unmapped column. Implement caching. |
| 1.6 | Pre-import preview with column selection/unselection | 🟡 Partial | `base_import` | "Test Import" button validates data. No column visibility toggle. | None | Add a wizard step: render column list with checkboxes; user deselects unwanted columns before processing | Extend native or new wizard | Medium | UX can be built as a transient model multi-step wizard |
| 1.7 | File size / row count limits enforcement | 🟡 Partial | `base_import` | Server-side memory limits apply (configurable via `--max-cron-threads`, server RAM). No user-facing row limit UI. | None | Add configurable system parameter `max_import_rows` + `max_file_size_mb`; validate in wizard before processing | Extend `ceo_campaign_automation` wizard | Low | Recommend: default 10,000 rows / 5 MB |
| 1.8 | ETL preprocessing (normalize data before import) | ❌ Not Native | None | No native ETL pipeline | None | Custom preprocessing layer in wizard (strip whitespace, normalize phone formats, uppercase names, detect encoding) | `ceo_campaign_automation` wizard preprocessing step | Medium | Can use Python `phonenumbers` library for phone normalization |
| 1.9 | Full `res.partner` Excel template (all fields) | ❌ Not Native | `base_import` | Downloadable template contains only 4–6 default columns. Not exhaustive. | None | Generate template dynamically via `fields_get()` on `res.partner`; write to XLSX using `openpyxl` and stream as attachment | New button in `ceo_campaign_automation` | Low | Filter out computed, readonly, and relational many2many fields for usability |

---

## PART 2 — Data Cleanup & Deduplication

| # | Feature / Requirement | Available Natively? | Existing Odoo Module(s) | Native Functionality | AI Features in Odoo 19 | Required Customization | Recommended Approach | Complexity | Notes / Risks |
|---|---|---|---|---|---|---|---|---|---|
| 2.1 | Duplicate detection on `res.partner` | ✅ Native ⭐ | `data_recycle` (Data Cleaning app) | Rule-based deduplication on Name, Email, Phone, VAT. Configurable field combinations. | None | None for standard rules | Use Data Cleaning app natively | Low | Enterprise only. Community lacks this module. |
| 2.2 | Fuzzy / similarity matching (typos, abbreviations) | 🟡 Partial ⭐ | `data_recycle` | Supports similarity threshold (0–100%). Uses string similarity algorithms (Levenshtein-based). | None native | For advanced NLP-based fuzzy matching (e.g. "SARL Bensmail" ≈ "Bensmail SARL"), custom scoring using `rapidfuzz` Python library | Extend Data Cleaning module or custom cron job | Medium | `rapidfuzz` not bundled with Odoo. Requires pip install on server. |
| 2.3 | Automatic duplicate merge | ✅ Native ⭐ | `data_recycle` | Auto-merge mode: records above threshold merged automatically without manual review. Configurable. | None | None | Use native auto-merge | Low | Irreversible. Recommend: always keep manual mode + audit log |
| 2.4 | Manual merge (select destination record) | ✅ Native | `contacts` / `base` | Action → Merge from list view. User selects master record. All related records (invoices, orders) transferred. | None | None | Native | Low | Native merge does not handle custom `x_` fields automatically — verify data transfer |
| 2.5 | Name normalization (case, spacing, formatting) | 🟡 Partial ⭐ | `data_recycle` | Data Cleaning app has "Formatting" rules: trim spaces, capitalize, etc. Limited to predefined patterns. | None | For advanced normalization (handling Arabic names, handling "SARL/EURL/SPA" suffixes, etc.) → custom `res.partner` onchange or post-import cron | Extend Data Cleaning or add server action | Medium | Algerian market: consider "Wilaya" normalization, Arabic transliteration |
| 2.6 | Post-import "fresh contact" tag auto-assignment | 🟡 Partial | `contacts` + `ceo_campaign_automation` | Odoo supports `category_id` (tags) on `res.partner`. Manual assignment possible. | None | Auto-assign tag "Source: Import Excel/CSV" during import wizard (already implemented in `ceo_campaign_automation`) | Already in `ceo_campaign_automation` ✅ | Low | Tags are visible as colored chips on contact cards natively |

---

## PART 3 — Contact Qualification Campaigns

| # | Feature / Requirement | Available Natively? | Existing Odoo Module(s) | Native Functionality | AI Features in Odoo 19 | Required Customization | Recommended Approach | Complexity | Notes / Risks |
|---|---|---|---|---|---|---|---|---|---|
| 3.1 | Email campaigns to contacts | ✅ Native | `mass_mailing` (Email Marketing) | Full campaign management: segments, templates, scheduling, A/B testing, statistics. | AI email body generation via Gemini/OpenAI (Odoo IAP) ⭐ | None for basic campaigns | Use native Email Marketing | Low | |
| 3.2 | WhatsApp campaigns | 🟡 Partial ⭐ | `whatsapp` (WhatsApp Business) | Native WhatsApp template message sending to contacts. Bulk send via Marketing Automation triggers. | None native for WhatsApp content generation | For bulk campaign-style WhatsApp flows: use Marketing Automation + WhatsApp action. No native campaign builder dedicated to WhatsApp. | Combine `whatsapp` + `marketing_automation` | Medium | Requires Meta Business API account + approved templates |
| 3.3 | SMS campaigns | ✅ Native ⭐ | `mass_mailing` / `sms` | Native SMS Marketing module. Segment contacts, schedule bulk SMS. Uses IAP credits or custom gateway (Twilio). | None | None for standard SMS | Use native SMS Marketing | Low | Cost: Odoo IAP SMS credits per message |
| 3.4 | Phone call campaigns / call scheduling | 🟡 Partial | `crm` / `phone` (VoIP) / `mass_mailing` | Marketing Automation can trigger "Create Activity → Phone Call". VoIP (Phone) app handles click-to-call + call logging. No native bulk call campaign builder. | None | Custom: "Call Campaign" wizard that generates bulk call activities per agent, with script display during call | New sub-module or extend `ceo_campaign_automation` | High |  |
| 3.5 | WhatsApp → SMS fallback (when number not on WA) | 🟡 Partial | `whatsapp` + `marketing_automation` | No native one-click fallback. Can be built with Marketing Automation conditional branches (if WA status = Failed → SMS step). | None | Custom server action: check WA delivery status via Meta API webhook → trigger SMS automatically | Extend `marketing_automation` + webhook handler | High | Meta API does not always return granular "not on WhatsApp" status. Timing of fallback is tricky. |
| 3.6 | Contact qualification scoring (data completeness) | 🟡 Partial | `crm` (Predictive Lead Scoring) | CRM has ML-based predictive scoring for **leads/opportunities**, NOT for raw contacts (`res.partner`). | ✅ ML-based scoring in CRM ⭐ — uses historical win/loss data | Custom scoring on `res.partner`: score fields for email validity, phone validity, company present, job title present, etc. Computed field `x_qualification_score` | Extend `res.partner` in `ceo_campaign_automation` | Medium | CRM predictive scoring only applies after contacts become leads. |
| 3.7 | Scoring from email campaign interactions (opens, clicks) | 🟡 Partial | `mass_mailing` | Email open/click tracking exists natively. Data stored in `mailing.trace`. | None | Custom: scheduled action reads `mailing.trace` for each partner → increments `x_qualification_score` | Extend `ceo_campaign_automation` with scoring cron | Medium | Pixel tracking (opens) blocked by many email clients (Apple Mail Privacy Protection) |
| 3.8 | Scoring from WhatsApp/SMS interactions | ❌ Not Native | None | WhatsApp read receipts exist in `discuss`. Not exposed for scoring. SMS has no response tracking. | None | Custom webhook listener for WhatsApp reply events → update score. SMS: track replies via Twilio webhook. | New webhook controller in `ceo_campaign_automation` | Very High | Requires Meta API webhook + custom response parsing |
| 3.9 | Scoring from phone call outcomes | ❌ Not Native | `phone` (VoIP) | Call duration and basic log stored. No outcome scoring native. | None | Custom: after call, agent selects outcome (Interested / Not Interested / No Answer) → score updated via wizard | Extend call activity form | Medium | Requires agent discipline in logging outcomes |

---

## PART 4 — Sales Campaigns & CRM Pipeline

| # | Feature / Requirement | Available Natively? | Existing Odoo Module(s) | Native Functionality | AI Features in Odoo 19 | Required Customization | Recommended Approach | Complexity | Notes / Risks |
|---|---|---|---|---|---|---|---|---|---|
| 4.1 | Lead / Opportunity pipeline management | ✅ Native | `crm` | Full Kanban pipeline with stages, won/lost, expected revenue, close date. | ✅ AI forecasting ⭐, deal health indicators | None | Use native CRM | Low | |
| 4.2 | Won / Lost tracking & reasons | ✅ Native | `crm` | Lost reason selection on close. Won date recorded. Reports available. | None | None | Native | Low | |
| 4.3 | Contact → Lead conversion | ✅ Native | `crm` + `contacts` | "Create Lead" button from `res.partner` record. | None | Can enrich with qualification score to auto-set lead priority | None or minor extension | Low | |
| 4.4 | Follow-up workflow automation | ✅ Native ⭐ | `marketing_automation` + `crm` | Marketing Automation can trigger on lead stage changes, send emails, create activities, assign leads. | None native | For advanced conditional logic (score-based routing), custom server actions | Use native + server actions | Low–Medium | |
| 4.5 | Predictive lead scoring (ML) | ✅ Native ⭐ | `crm` | Uses ML trained on historical data. Probability 0–100% updated dynamically. Auto-assigns to teams based on score. | ✅ ML model built-in (Odoo IAP) | None | Native | Low | Requires sufficient historical data (>100 won/lost) to be accurate |
| 4.6 | "Next best action" recommendations | ✅ Native ⭐ | `crm` | AI suggests next action based on pipeline analysis | ✅ AI-powered in Odoo 19 | None | Native | Low | |
| 4.7 | Sales campaign reporting / dashboards | ✅ Native | `crm` + `mass_mailing` | Built-in CRM reporting: pipeline, conversion rates, salesperson performance. Email stats: opens, clicks, bounces. | None | None for standard | Native | Low | |
| 4.8 | Campaign-to-pipeline traceability | 🟡 Partial | `crm` + `mass_mailing` | Email campaigns can create leads from CTA clicks (UTM tracking). Not fully connected to WhatsApp/SMS/Call campaigns. | None | Custom: tag leads with campaign source; enrich with channel (WA/SMS/call) and score at conversion | Extend `crm` + `ceo_campaign_automation` | Medium | |

---

## PART 5 — AI Content Generation & Smart Follow-Up

| # | Feature / Requirement | Available Natively? | Existing Odoo Module(s) | Native Functionality | AI Features in Odoo 19 | Required Customization | External API Needed? | Recommended Approach | Complexity | Notes / Risks |
|---|---|---|---|---|---|---|---|---|---|---|
| 5.1 | AI email body generation (per campaign) | ✅ Native ⭐ | `mass_mailing` / `mail` | "Generate Email" button using Odoo IAP (OpenAI/Gemini under the hood) | ✅ Native (Odoo IAP credits) | None for generic generation. For campaign-theme-aware generation: pass context (theme, contact profile) as prompt | None (use IAP) or Gemini API directly | Use native IAP or direct Gemini API (as in `ceo_campaign_automation`) | Low–Medium | Odoo IAP costs credits. Direct Gemini API = cheaper + more control |
| 5.2 | AI phone call script generation (per contact) | ❌ Not Native | None | No native call script generation | None for call scripts | Custom: call script wizard → sends contact profile + campaign theme to Gemini API → returns formatted script displayed during VoIP call | ✅ Gemini / OpenAI API | New module or extend `ceo_campaign_automation` + VoIP activity form | High | Script must be dynamic: adapt per contact interests, past interactions, campaign |
| 5.3 | Personalized email per contact (not per group) | 🟡 Partial ⭐ | `mass_mailing` | Supports dynamic content using `{{ object.name }}` Jinja2 placeholders. Not fully AI-personalized per contact. | 🟡 AI can generate template but not unique per-contact body at send time | Custom: pre-generate email body per contact batch via Gemini → store in custom field → use as email template variable | ✅ Gemini API | Extend `mass_mailing` + `ceo_campaign_automation` | Very High | N API calls = N contacts. Cost + latency concern for large lists. |
| 5.4 | Email open / click tracking | ✅ Native | `mass_mailing` | Pixel tracking for opens, click tracking via redirect links. Stats in `mailing.trace`. | None | None | Native | Low | Opens increasingly unreliable (Apple MPP, corporate firewalls) |
| 5.5 | Hard / soft bounce handling | ✅ Native | `mass_mailing` | Native bounce detection. Hard bounce: contact blacklisted. Soft bounce: retry logic. `mail.blacklist` model. | None | None | Native | Low | |
| 5.6 | Engagement tracking → score update | ❌ Not Native | `mass_mailing` | Stats stored in `mailing.trace`. Not connected to a contact score. | None | Custom scheduled action: parse `mailing.trace` → update `x_qualification_score` on `res.partner` | None (internal) | Extend `ceo_campaign_automation` | Medium | |
| 5.7 | Callback reminder ("call me back on date X") | 🟡 Partial | `crm` / `phone` | CRM activity scheduling exists. Not linked to WhatsApp/email conversations automatically. | None | Custom: parse inbound WhatsApp/email for callback intent → create CRM activity with date. Can use Gemini to extract date from natural language message. | ✅ Gemini API (NLP extraction) | Extend `discuss` + `crm` with Gemini NLP trigger | High | |
| 5.8 | AI-based "who to call first" recommendation | ❌ Not Native | None | CRM predictive scoring ranks opportunities, not raw contacts for calling. | 🟡 CRM scoring is close but limited to pipeline | Custom scoring engine: combine `x_qualification_score` + engagement level + campaign theme affinity + last interaction date → ranked list with explanation | ✅ Gemini for explanation text | New module or dedicated dashboard in `ceo_campaign_automation` | High | |
| 5.9 | Dynamic phone script adapted to interests | ❌ Not Native | None | No native adaptive call script | None | Custom: before call, fetch contact's `x_qualification_score`, campaign, tags, past email open topics → compose prompt → Gemini generates script | ✅ Gemini API | Extend VoIP activity + `ceo_campaign_automation` | Very High | |

---

## Summary Matrix

| Area | Native Coverage | Development Effort |
|------|----------------|-------------------|
| **1. Import & Smart Mapping** | 30% | High — core differentiator requiring custom work |
| **2. Deduplication & Cleanup** | 75% ⭐ | Low–Medium — Data Cleaning covers most needs |
| **3. Qualification Campaigns** | 60% ⭐ | High — WhatsApp fallback, scoring, call campaigns |
| **4. CRM Pipeline & Sales** | 85% ⭐ | Low — mostly native with minor extensions |
| **5. AI Content & Smart Follow-up** | 40% ⭐ | Very High — core AI features require external API |

---

## Recommended Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ODOO 19 ENTERPRISE                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              NATIVE ODOO MODULES (No or minimal config)              │   │
│  │  • Contacts (res.partner)    • CRM (Predictive Scoring + Pipeline)  │   │
│  │  • Email Marketing            • WhatsApp Business                   │   │
│  │  • SMS Marketing              • Marketing Automation                │   │
│  │  • Phone / VoIP               • Data Cleaning (Deduplication)       │   │
│  │  • AI Agents (Meeting transcription, Ask AI, Email generation IAP)  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │         ceo_campaign_automation  (Custom Module — Primary)           │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │   │
│  │  │ Import Engine  │  │  Scoring Engine   │  │  AI Content Engine │  │   │
│  │  │                │  │                   │  │                    │  │   │
│  │  │ • CSV/Excel    │  │ x_qualification_  │  │ • Email generation │  │   │
│  │  │   parsing      │  │   score computed  │  │ • Call script gen. │  │   │
│  │  │ • Heuristic    │  │   field on        │  │ • "Who to call"    │  │   │
│  │  │   column map   │  │   res.partner     │  │   ranking engine   │  │   │
│  │  │ • Gemini AI    │  │                   │  │ • Callback intent  │  │   │
│  │  │   mapping      │  │ • Data completeness   detection          │  │   │
│  │  │ • Dynamic      │  │ • Email engagement│  │                    │  │   │
│  │  │   field create │  │ • Call outcomes   │  │  ↕ Gemini Flash API│  │   │
│  │  │ • Row preview  │  │ • WA/SMS replies  │  └────────────────────┘  │   │
│  │  │ • Import limits│  └──────────────────┘                           │   │
│  │  └────────────────┘                                                  │   │
│  │                                                                      │   │
│  │  ┌────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │   │
│  │  │ Campaign       │  │  Multi-Channel   │  │  Reporting &       │  │   │
│  │  │ Orchestrator   │  │  Fallback Logic  │  │  Dashboard         │  │   │
│  │  │                │  │                  │  │                    │  │   │
│  │  │ (extends       │  │ WA→SMS→Call      │  │ Qualified contacts │  │   │
│  │  │  marketing_    │  │ fallback via     │  │ by campaign        │  │   │
│  │  │  automation)   │  │ webhook + server │  │ Call script logs   │  │   │
│  │  │                │  │ action chains    │  │ Score distribution │  │   │
│  │  └────────────────┘  └──────────────────┘  └────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              EXTERNAL INTEGRATIONS                                   │   │
│  │  • Google Gemini 1.5 Flash API (Column mapping, Email/Script gen.)  │   │
│  │  • Meta WhatsApp Business API (Webhook for delivery/reply status)   │   │
│  │  • Twilio / SMS Gateway (Delivery reports + reply webhooks)         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Technical Decisions

> [!IMPORTANT]
> **Single Custom Module Strategy:** All custom logic should live in `ceo_campaign_automation`. Do NOT scatter code across multiple micro-modules. This module acts as the **CRM Intelligence Layer** sitting on top of standard Odoo.

---

## Odoo 19 Enterprise Modules Required

| Module | Purpose | Edition |
|--------|---------|---------|
| `contacts` | `res.partner` storage | Community + Enterprise |
| `base_import` | Native CSV/Excel import | Community + Enterprise |
| `crm` | Pipeline, lead scoring | Community + Enterprise |
| `mass_mailing` | Email + SMS campaigns | Community + Enterprise |
| `marketing_automation` | Multi-step campaign orchestration | **Enterprise Only** |
| `whatsapp` | WhatsApp Business API integration | **Enterprise Only** |
| `sms` | Native SMS gateway | Community + Enterprise |
| `phone` / `voip` | VoIP call logging + click-to-call | **Enterprise Only** |
| `data_recycle` | Deduplication (Data Cleaning app) | **Enterprise Only** |
| `studio` | No-code custom field creation (alternative) | **Enterprise Only** |
| `mail` / AI Agents | Odoo AI Agents + meeting transcription | **Enterprise Only** |
