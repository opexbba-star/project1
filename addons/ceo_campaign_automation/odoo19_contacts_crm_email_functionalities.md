# Odoo 19 — Native Functionality Catalog: Contacts · CRM · Email Marketing

> **Scope:** Odoo 19 (Community + Enterprise) | **Modules:** Contacts (`contacts`/`base`), CRM (`crm`), Email Marketing (`mass_mailing`) and their direct companions
> **Purpose:** Reference catalog of *what is available natively* in each edition — companion to `odoo19_crm_analysis.md` (which covers the custom-development gap analysis)
> **Date:** June 2026 | **Basis:** Odoo 19.0 official documentation + Odoo 19 release notes (OXP 2025)

---

## Legend

| Symbol | Meaning |
|--------|---------|
| 🟢 | Community + Enterprise (free / open source core) |
| ⭐ | Enterprise Edition only |
| 💳 | Requires Odoo IAP credits or a paid external gateway (works in the edition shown, but consumes credits) |
| 🤖 | New or enhanced **AI** capability in Odoo 19 |
| 🔧 | Configurable but functionally limited natively |

> **Edition rule of thumb:** Community and Enterprise share the **same database schema and ORM**. Enterprise adds polished UI, mobile apps, AI/IAP services, and a set of premium apps. A Community DB can be upgraded to Enterprise in place. Always confirm the exact split against your deployed 19.x point release — Odoo occasionally shifts features between editions, and IAP/AI features depend on an active IAP account.

---

## PART 1 — Contacts (`res.partner`)

### 1A. Core Records & Data Model

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 1.1 | Company & Individual contacts | 🟢 | `contacts` / `base` | Single `res.partner` model stores companies, individuals, and contacts-of-companies via `is_company` + `parent_id` hierarchy. | One model powers every app's partner reference (sales, invoicing, CRM, mailing). |
| 1.2 | Multiple addresses per contact | 🟢 | `contacts` | Child addresses typed as Contact, Invoice, Delivery, Other, Private, Follow-up. | Invoice/Delivery addresses auto-propagate to sales/invoicing. |
| 1.3 | Contact tags / categories | 🟢 | `contacts` | `category_id` (many2many) with colored chips; used for segmentation and mailing filters. | Hierarchical tags supported. |
| 1.4 | Company ↔ contact hierarchy | 🟢 | `contacts` | `parent_id` / `child_ids`; org-chart style relations. | Address inheritance from parent company. |
| 1.5 | Communication fields | 🟢 | `contacts` | Email, phone, mobile, website, job position, title, language, timezone. | Phone/mobile feed VoIP & SMS. |
| 1.6 | Bank accounts | 🟢 | `account` (on partner) | `res.partner.bank` records for payments. | Validated against country formats. |
| 1.7 | VAT / Tax ID validation | 🟢 | `base_vat` | Validates VAT numbers against country syntax (and VIES where applicable). | Algeria: NIF/RC/AI handled via localization fields, not EU-VIES. |
| 1.8 | Industry classification | 🟢 | `base` | `industry_id` standard taxonomy. | Useful for CRM/mailing segmentation. |
| 1.9 | Internal notes & custom fields | 🟢 | `base` / Studio ⭐ | Notes tab + ability to add fields. Code-free field creation needs **Studio ⭐**; otherwise developer/`ir.model.fields`. | See `odoo19_crm_analysis.md` §1.4 for dynamic import-time field creation. |
| 1.10 | Mailing / marketing preferences | 🟢 | `mail` | Email/SMS opt-out, blacklist link, marketing consent. | Drives `mail.blacklist`. |
| 1.11 | Documents & chatter | 🟢 | `mail` | Activity log, messages, followers, attachments on every contact. | Audit trail of all interactions. |

### 1B. Enrichment, Geolocation & AI

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 1.12 | Partner autocomplete / company enrichment | 🟢 💳 | `partner_autocomplete` | Type a company name → auto-fills legal name, logo, address, VAT, etc. from Odoo's data service. | IAP credits per lookup; coverage weak for Algerian SMEs. |
| 1.13 | Geolocation | 🟢 💳 | `base_geolocalize` | Computes lat/long from address for map views & geo-assignment. | Uses a geocoding provider (IAP/Google key). |
| 1.14 | Business-card / document scanning → contact | ⭐ 🤖 💳 | AI / Documents | Scan a business card or document; AI extracts contact fields and creates the `res.partner`. | New in Odoo 19 AI workflow; IAP-based. |
| 1.15 | Automatic field completion (AI) | ⭐ 🤖 | AI Agents | AI suggests/fills fields from context. | Part of Odoo 19 AI layer. |

### 1C. Data Cleanup & Deduplication

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 1.16 | Manual merge of duplicates | 🟢 | `contacts` | List view → Action → *Merge*; pick master record, related docs (orders, invoices, mail) re-pointed. | Verify custom `x_` fields transfer. |
| 1.17 | Rule-based duplicate detection | ⭐ | `data_merge` (Data Cleaning) | Configurable rules on Name/Email/Phone/VAT with similarity threshold; review queue or auto-merge. | The dedup engine is `data_merge` (the `data_recycle` module handles record recycling/archival). |
| 1.18 | Field formatting / normalization rules | ⭐ | `data_recycle` / Data Cleaning | Trim spaces, fix case, standardize formats via recurring rules. | Limited to predefined patterns; advanced (Arabic, SARL/EURL suffixes) needs custom. |
| 1.19 | Record recycling (stale-record cleanup) | ⭐ | `data_recycle` | Auto-flag/archive records matching age/inactivity rules. | Good for hygiene of large imported lists. |

---

## PART 2 — CRM (`crm`)

### 2A. Pipeline & Lead Management

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 2.1 | Leads & Opportunities | 🟢 | `crm` | Two-stage funnel: Leads (raw) → Opportunities (qualified). Lead stage can be toggled on/off per team. | |
| 2.2 | Kanban pipeline with stages | 🟢 | `crm` | Drag-and-drop stages, expected revenue, probability, expected closing, color/priority. | Fully configurable stages. |
| 2.3 | Multiple sales teams & channels | 🟢 | `crm` / `sales_team` | Teams with their own pipelines, members, targets. | Team-scoped reporting. |
| 2.4 | Activities & scheduling | 🟢 | `mail` (activities) | Schedule calls, meetings, to-dos, emails on any lead; activity types & plans. | Feeds "My Activities" dashboard. |
| 2.5 | Lost reasons & Won tracking | 🟢 | `crm` | Mark Won/Lost with required Lost Reason; won date & revenue recorded. | Standard reporting on win/loss. |
| 2.6 | Contact → Lead/Opportunity conversion | 🟢 | `crm` + `contacts` | Create opportunity directly from a contact; partner auto-linked. | |
| 2.7 | Email & website lead generation | 🟢 | `crm` / `website_crm` | Inbound emails to an alias and website contact forms create leads. | |
| 2.8 | Live Chat → lead generation | ⭐ 🤖 | `livechat` + `crm` | Live chat / AI chat agents can auto-create qualified leads from conversations. | Enhanced in Odoo 19. |
| 2.9 | Recurring revenue (MRR) | 🟢 | `crm` | Recurring plans on opportunities for subscription-style forecasting. | |

### 2B. Scoring, Assignment & AI

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 2.10 | Predictive lead scoring (ML) | 🟢 | `crm` | Win-probability % computed from historical won/lost data; configurable variables. | Available in **Community too**; accuracy needs >100 closed leads. |
| 2.11 | Rules-based lead assignment | ⭐ 🤖 | `crm` | Auto-route leads by domain rules (region, language, priority, team capacity) on a recurring schedule; AI-supported in Odoo 19. | Manual assignment is 🟢; the automated rule engine is ⭐. |
| 2.12 | AI insights / next-best-action | ⭐ 🤖 | `crm` + AI | Win-probability insights and recommendations on which leads to prioritize. | Part of Odoo 19 AI layer. |
| 2.13 | Lead mining (generate new leads) | 🟢 💳 | `crm_iap_mine` | Generate net-new company/contact leads by country, industry, size. | IAP credits per lead; data coverage varies by region. |
| 2.14 | Lead enrichment | 🟢 💳 | `crm_iap_enrich` | Enrich existing leads with company data from email/domain. | IAP credits. |
| 2.15 | Natural-language pipeline search | ⭐ 🤖 | AI | Type queries in plain language → converted to domain filters on the pipeline. | New Odoo 19 capability. |

### 2C. Reporting & Forecasting

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 2.16 | Pipeline analysis (pivot/graph/list) | 🟢 | `crm` | Built-in pivot, graph, cohort-style reporting on pipeline, conversion, salesperson performance. | |
| 2.17 | Forecast view | 🟢 | `crm` | Expected-revenue forecast by expected closing month. | |
| 2.18 | Spreadsheet dashboards | ⭐ | `spreadsheet_dashboard` | Live, editable spreadsheet dashboards combining CRM data. | Community gets standard reporting only. |
| 2.19 | Quotation/document customization from CRM | ⭐ | `sale` integration | Customize quote sections, hide prices/sections per deal. | Odoo 19 quotation flexibility. |

---

## PART 3 — Email Marketing (`mass_mailing`)

### 3A. Campaign Creation & Design

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 3.1 | Mass email campaigns | 🟢 | `mass_mailing` | Full mailing creation: subject, recipients, body, scheduling, sending. | Email Marketing app is **Community**. |
| 3.2 | Drag-and-drop email designer | 🟢 | `mass_mailing` | Block-based responsive editor + starter themes. | |
| 3.3 | Mailing themes / templates | 🟢 | `mass_mailing_themes` | Pre-built responsive templates. | |
| 3.4 | Recipients: any model + filters | 🟢 | `mass_mailing` | Target `res.partner`, leads, mailing lists, event attendees, etc. with saved domain filters. | Powerful segmentation via filters. |
| 3.5 | Mailing lists & contacts | 🟢 | `mass_mailing` | Dedicated `mailing.list` / `mailing.contact` with subscribe/unsubscribe. | Separate from `res.partner`. |
| 3.6 | Dynamic placeholders (Jinja/QWeb) | 🟢 | `mass_mailing` | Personalize with `{{ object.name }}`-style fields and conditional content. | Per-field, not per-contact AI body — see analysis §5.3. |
| 3.7 | AI email content generation | ⭐ 🤖 💳 | `mass_mailing` / `mail` + AI | "Generate"/AI commands draft, rewrite, optimize, translate, summarize email copy. | IAP credits; new AI commands in Odoo 19 templates. |
| 3.8 | A/B testing | 🟢 | `mass_mailing` | Send variants to a % of recipients; winner (by opens/clicks) sent to the remainder. | Configured in the *A/B Tests* tab of the mailing. |

### 3B. Sending, Tracking & Deliverability

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 3.9 | Scheduling & throttling | 🟢 | `mass_mailing` | Schedule send time; queued via cron; rate-limited by server config. | |
| 3.10 | Open / click tracking | 🟢 | `mass_mailing` | Pixel-based opens + redirect-based click tracking stored in `mailing.trace`. | Opens unreliable (Apple MPP, corporate proxies). |
| 3.11 | UTM campaign tracking | 🟢 | `utm` | Campaign / source / medium tagging; links mailings to leads & sales. | Powers campaign-to-pipeline traceability. |
| 3.12 | Link tracker & statistics | 🟢 | `link_tracker` | Per-link click counts, geo, referrer. | |
| 3.13 | Real-time statistics | 🟢 | `mass_mailing` | Sent, delivered, opened, clicked, bounced, replied, plus generated leads/orders/revenue. | Dashboards per mailing & campaign. |
| 3.14 | Bounce handling & blacklist | 🟢 | `mass_mailing` / `mail` | Hard bounce → blacklist; soft bounce retry; `mail.blacklist` model + unsubscribe page. | |
| 3.15 | Unsubscribe / opt-out management | 🟢 | `mass_mailing` | Built-in unsubscribe landing + reason capture. | GDPR-friendly. |

### 3C. Multi-Channel & Automation

| # | Feature | Edition | Module | Description | Notes |
|---|---|---|---|---|---|
| 3.16 | SMS Marketing | 🟢 💳 | `mass_mailing_sms` / `sms` | Bulk SMS campaigns to segmented recipients; same stats framework. | IAP SMS credits or external gateway (e.g., Twilio). |
| 3.17 | Marketing Automation (drip flows) | ⭐ | `marketing_automation` | Multi-step, time-based, action-triggered campaigns (open/click/form → next step, branching). Installing it pulls in Email Marketing. | The orchestration engine; Email Marketing alone has no drip builder. |
| 3.18 | WhatsApp campaigns | ⭐ 💳 | `whatsapp` | Template-based WhatsApp Business messaging; bulk via Marketing Automation actions. | Needs Meta Business API + approved templates. |
| 3.19 | Social Marketing | ⭐ 💳 | `social` | Schedule/publish/monitor social posts and ads alongside email. | |
| 3.20 | Push notifications | ⭐ | `social_push_notifications` | Web push as a marketing channel. | |

---

## Edition Summary Matrix

| Module area | Community covers | Enterprise adds |
|------------|------------------|-----------------|
| **Contacts** | Full data model, tags, hierarchy, VAT validation, manual merge, autocomplete/geo (IAP) | Data Cleaning (rule-based dedup/normalize/recycle), AI field completion, card/document scanning |
| **CRM** | Pipeline, teams, activities, won/lost, predictive scoring, lead mining/enrichment (IAP), pivot/graph reporting, forecast | Rules-based + AI lead assignment, AI insights/next-best-action, NL pipeline search, live-chat lead gen, spreadsheet dashboards |
| **Email Marketing** | Campaigns, drag-drop designer, A/B testing, segmentation, open/click/UTM tracking, bounce/blacklist, SMS (IAP) | Marketing Automation (drip), WhatsApp, Social Marketing, AI content generation |

---

## Odoo 19 AI Layer (cross-module, ⭐ 💳)

Odoo 19 is the first release to weave AI across the workflow. Capabilities touching these three modules:

- **AI Agents** — assistants trained on your Odoo data that can create records, update fields, and send emails.
- **Natural-language search** — plain-language queries converted to domain filters (e.g., on the CRM pipeline).
- **Automatic field completion** — AI fills contact/lead fields from context.
- **Lead generation** — AI + business-card scanning + live-chat agents auto-create leads.
- **AI email commands** — draft, rewrite, optimize, translate, and summarize directly in email templates.
- **Meeting transcription & summaries** — real-time transcripts with auto-summaries feeding CRM activities.
- **Voice-to-text** — dictate into fields/notes.

> All AI features depend on an active **Odoo IAP** account and consume credits. Availability and exact behavior vary by 19.x point release — verify against your deployment before committing to a design.

---

## Modules Reference

| Module | Area | Edition |
|--------|------|---------|
| `contacts` / `base` | Contact storage & data model | 🟢 |
| `base_vat` | VAT/Tax ID validation | 🟢 |
| `partner_autocomplete` | Company enrichment (IAP) | 🟢 💳 |
| `base_geolocalize` | Geolocation | 🟢 💳 |
| `data_merge` | Deduplication engine (Data Cleaning) | ⭐ |
| `data_recycle` | Record recycling / normalization rules | ⭐ |
| `crm` | Pipeline, scoring, assignment | 🟢 (assignment engine ⭐) |
| `crm_iap_mine` | Lead mining | 🟢 💳 |
| `crm_iap_enrich` | Lead enrichment | 🟢 💳 |
| `sales_team` | Sales teams | 🟢 |
| `spreadsheet_dashboard` | Live dashboards | ⭐ |
| `mass_mailing` | Email Marketing (incl. A/B testing) | 🟢 |
| `mass_mailing_themes` | Mailing templates | 🟢 |
| `mass_mailing_sms` / `sms` | SMS Marketing | 🟢 💳 |
| `utm` / `link_tracker` | Campaign & link tracking | 🟢 |
| `mail` | Chatter, activities, blacklist | 🟢 |
| `marketing_automation` | Drip/orchestration | ⭐ |
| `whatsapp` | WhatsApp Business | ⭐ 💳 |
| `social` | Social Marketing | ⭐ 💳 |
| AI Agents / IAP | Cross-module AI layer | ⭐ 💳 |

---

## Sources

- [Odoo 19.0 — Email Marketing documentation](https://www.odoo.com/documentation/19.0/applications/marketing/email_marketing.html)
- [Odoo 19.0 — Marketing Automation documentation](https://www.odoo.com/documentation/19.0/applications/marketing/marketing_automation.html)
- [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [Odoo Editions Comparison (Community vs Enterprise)](https://www.odoo.com/page/editions)
- [Odoo 19 Features & Updates — Technaureus](https://www.technaureus.com/blog-detail/odoo-19-features-updates-whats-new-in-2025-release)
- [Odoo 19 Community vs Enterprise — MoonSun](https://www.moonsun.au/blog/moonsun-mag-1/odoo-19-community-vs-enterprise-166)

> ⚠️ **Verification note:** Edition splits and AI/IAP behavior were validated against Odoo 19.0 documentation and 2025 release coverage as of June 2026. Confirm against your specific 19.x deployment and active IAP subscription before architectural commitments.
