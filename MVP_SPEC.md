# MVP Spec — Launch Attribution Dashboard (2 Weeks)

## 1) Scope
Build a minimal analytics product with three capabilities:
1. **UTM Ingestion**
2. **Source Conversion Dashboard**
3. **Basic Cohort View**

## 2) Functional Requirements

### FR-1 Event Ingestion API
- Endpoint: `POST /api/events`
- Accept JSON payload with:
  - `event_name` (e.g., `visit`, `signup`, `activated`, `purchase`)
  - `event_time` (ISO timestamp)
  - `user_id` (required for conversion/cohort events)
  - `session_id` (optional but recommended)
  - `utm_source`, `utm_medium`, `utm_campaign` (optional, normalized)
  - `utm_content`, `utm_term` (optional)
  - `properties` (object, optional)
- Validate schema; return 4xx on malformed requests.
- Store raw + normalized fields.

### FR-2 Attribution Model (MVP)
- First-touch attribution per user:
  - First known UTM source/campaign tied to a user becomes attribution source.
  - If unknown, classify as `direct/unknown`.
- Conversion events (`signup`, `activated`, `purchase`) map to first-touch source.

### FR-3 Source Conversion Dashboard
- Time range selector (7d, 30d, custom)
- Table/cards by source/campaign:
  - Visits
  - Signups
  - Activated users (or purchase if enabled)
  - Conversion rates (`visit->signup`, `signup->activated`)
- Sort by conversions and conversion rate.

### FR-4 Basic Cohort View
- Cohort type: **first signup date** (daily, optional weekly toggle)
- Rows: cohort date
- Columns: D0, D1, D7 (minimum) activation/return indicator
- Segment filter: source/campaign

### FR-5 Project/Workspace Baseline
- Single workspace model for MVP
- API key auth for ingestion
- Basic dashboard access control (single owner/admin login acceptable)

### FR-6 Documentation
- Quickstart:
  - Generate API key
  - Send sample UTM events
  - Read conversion + cohort dashboard
- Event schema reference

## 3) Non-Functional Requirements
- p95 ingestion response time: < 400ms
- Event pipeline latency to dashboard: < 60s p95
- Availability target during MVP test: 99%
- Auditability: raw event log retained

## 4) Data Model (Minimal)

### events
- `id`
- `event_name`
- `event_time`
- `user_id`
- `session_id`
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- `properties_json`
- `received_at`

### user_attribution
- `user_id` (PK)
- `first_touch_time`
- `first_utm_source`
- `first_utm_medium`
- `first_utm_campaign`

### daily_metrics (materialized/derived)
- `date`
- `source`
- `campaign`
- `visits`
- `signups`
- `activated`

## 5) Analytics Definitions (MVP)
- **Visit:** event_name = `visit`
- **Signup:** event_name = `signup`
- **Activated:** event_name = `activated` (or `purchase` if product-specific)
- **Visit→Signup CVR:** signups / visits
- **Signup→Activated CVR:** activated / signups

## 6) 2-Week Delivery Plan

### Week 1
- Day 1–2: ingestion endpoint + schema validation + storage
- Day 3: attribution job (first-touch mapping)
- Day 4: metrics aggregation + test dataset
- Day 5: initial conversion dashboard

### Week 2
- Day 6–7: cohort computation + cohort UI
- Day 8: auth/API key + filters/range selector
- Day 9: QA, instrumentation, docs
- Day 10: bug fixes + MVP release + KPI baseline

## 7) Acceptance Criteria
- Can ingest valid UTM-tagged events via API and reject malformed payloads
- Dashboard shows source/campaign conversion metrics for selectable date ranges
- Cohort table renders D0/D1/D7 for signup cohorts
- Attribution mapping is consistent for first-touch model
- Quickstart allows a new user to see data in dashboard in <30 min
