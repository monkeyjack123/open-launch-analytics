# Backlog — MVP (First 10 Issues)

## Milestone: v0.1 (2-week MVP)

### Issue 1 — Define event schema and validation rules
**Type:** Backend
**Priority:** P0
**Description:** Finalize canonical event contract (required/optional fields, enums, timestamp formats, error responses).
**Acceptance Criteria:**
- JSON schema checked into repo
- Validation middleware enforces schema
- Invalid payload returns structured 400 with field-level error

### Issue 2 — Build ingestion API endpoint (`POST /api/events`)
**Type:** Backend
**Priority:** P0
**Description:** Implement endpoint for event ingestion with API key auth and persistence.
**Acceptance Criteria:**
- Authenticated ingestion works end-to-end
- Events persisted with raw + normalized UTM fields
- Throughput tested for MVP load profile

### Issue 3 — UTM normalization and fallback handling
**Type:** Backend/Data
**Priority:** P0
**Description:** Normalize casing/whitespace and map missing values to `direct/unknown`.
**Acceptance Criteria:**
- Normalization rules documented and tested
- Unknown/missing values consistently bucketed
- Dashboard uses normalized dimensions

### Issue 4 — First-touch attribution table/job
**Type:** Data
**Priority:** P0
**Description:** Create per-user first-touch attribution from earliest known UTM-tagged event.
**Acceptance Criteria:**
- `user_attribution` table populated incrementally
- Deterministic logic with tests
- Conversions can join attribution data reliably

### Issue 5 — Conversion metrics aggregation pipeline
**Type:** Data
**Priority:** P0
**Description:** Aggregate visits/signups/activations by date/source/campaign.
**Acceptance Criteria:**
- Daily metrics table/materialized view available
- Core conversion rates computed correctly
- Recompute/backfill script exists for date range

### Issue 6 — Source conversion dashboard UI
**Type:** Frontend
**Priority:** P0
**Description:** Build dashboard with key metric cards + breakdown table by source/campaign.
**Acceptance Criteria:**
- 7d/30d/custom filters
- Sort and basic filtering
- Metrics align with aggregation pipeline outputs
**Progress (2026-03-09):**
- Added backend helper `summarize_funnel(...)` to power key metric cards with date/source/campaign filters.
- Added backend helper `build_funnel_breakdown(...)` to power source/campaign table rows with filter/sort/limit behavior.
- Added `resolve_date_range(...)` to support dashboard `7d`/`30d`/`custom` filter presets with strict validation.
- Added tests and API contract docs for breakdown + date preset backend (`docs/funnel-breakdown.md`, `docs/date-range-presets.md`).
- Added `build_dashboard_filter_options(...)` to provide deterministic source/campaign dropdown options with event-volume ordering for UI controls.
- Added tests for filter-option count/sort behavior and date-validation guardrails.
- Added backend contract docs for dashboard control wiring (`docs/dashboard-filter-options.md`).
- Added `build_funnel_timeseries(...)` helper to provide day-level visits/signups/activations rows with optional zero-fill between explicit date bounds for chart rendering.
- Remaining: ship UI rendering layer and wire interactive controls to summary/breakdown/date-range/filter-option/timeseries helpers.

### Issue 7 — Basic cohort view (D0/D1/D7)
**Type:** Frontend/Data
**Priority:** P1
**Description:** Implement signup cohorts and show activation/return rates per cohort.
**Acceptance Criteria:**
- Cohort matrix renders correctly for test and real data
- Supports filter by source/campaign
- Clear legend/definition in UI
**Progress (2026-03-09):**
- Added `build_cohort_matrix(...)` envelope to provide table `columns`, `rows`, day `legend`, and weighted `totals` footer for direct UI rendering.
- Hardened day-offset input handling (non-negative validation + deterministic de-dupe/sort).
- Added tests for matrix metadata/totals and invalid day input handling.
- Updated cohort docs with matrix contract and explicit D0/D1/D7 legend semantics.

### Issue 8 — API key management + minimal auth
**Type:** Platform/Security
**Priority:** P1
**Description:** Provide single-workspace auth and API key generation/rotation.
**Acceptance Criteria:**
- Owner can create/revoke ingestion keys
- Unauthorized requests rejected (401/403)
- Secrets not exposed in logs/UI
**Progress (2026-03-09):**
- Added `ApiKeyManager` with owner lifecycle helpers: `create_key`, `rotate_key`, `revoke_key`, and metadata-only `list_keys`.
- Added digest-mode auth path with `validate_api_key_hash(...)` + `active_key_hashes()` for secure key validation without plaintext storage.
- Added tests for create/rotate/revoke flows and non-leaking list output (redacted previews only).
- Updated auth contract docs with lifecycle + hash-validation guidance.

### Issue 9 — QA, observability, and data quality checks
**Type:** QA/DevOps
**Priority:** P1
**Description:** Add health checks, ingestion error logging, and attribution completeness monitor.
**Acceptance Criteria:**
- Basic dashboard/API health endpoint
- Error-rate and latency metrics visible
- Daily data-quality report (missing UTM %, invalid payload %)
**Progress (2026-03-10):**
- Added `build_attribution_completeness_report(events, conversion_events=None)` for conversion-level attribution coverage monitoring.
- Report now exposes `conversions`, `attributed_conversions`, `unattributed_conversions`, and `attribution_match_rate` for KPI tracking.
- Added tests for default conversion set (`signup`/`activation`), custom conversion events, and conversion event input validation.
- Added `build_ingestion_slo_report(samples, max_error_rate, max_p95_latency_ms)` to track request-level error-rate + p95 latency against explicit SLO thresholds.
- Added tests covering degraded p95 latency posture, empty telemetry sets, and invalid/missing latency sample handling.
- Updated quality docs to include attribution completeness report contract and KPI usage notes.

### Issue 10 — Quickstart docs + sample data + release checklist
**Type:** Docs/Release
**Priority:** P1
**Description:** Make MVP easy to trial with sample curl events and setup steps.
**Acceptance Criteria:**
- `README` updated with quickstart
- Sample script posts test events
- Release checklist completed and signed off

---

## MVP KPI Tracking (linked to launch criteria)

1. **Ingestion success rate** ≥ 99.5%
2. **Dashboard freshness (p95)** < 60s
3. **Attribution match rate** ≥ 90% of conversions mapped to first-touch source
4. **Time-to-first-insight** < 30 min from setup
5. **Activation** ≥ 60% of workspaces send 100+ events in 48h
6. **Weekly engagement** ≥ 40% of activated workspaces open dashboard 2+ times/week

## Out of Scope for v0.1
- Multi-touch attribution
- Ad spend integrations
- Advanced retention/cohort slicing beyond D0/D1/D7
- Multi-tenant enterprise permissions
