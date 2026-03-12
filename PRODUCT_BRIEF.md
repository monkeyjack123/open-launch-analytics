# Product Brief — Open Launch Analytics (2-Week MVP)

## 1) Product Summary
Open Launch Analytics is a lightweight dashboard that answers one core question for early-stage launches:

**“Which acquisition sources and campaigns are actually converting?”**

This MVP focuses on:
1. **UTM ingestion** from inbound traffic/events
2. **Source-to-conversion reporting** (channel/campaign performance)
3. **Basic cohort view** (day/week cohorts by first-touch source)

## 2) Problem
Launch teams run multiple channels (X, LinkedIn, Product Hunt, newsletters, communities, paid tests), but attribution is fragmented across tools. Teams can’t quickly see:
- Which source drives signups
- Which source drives activation/conversion
- Whether conversion quality holds over time

## 3) Target Users
- **Primary:** Solo founders, indie hackers, small growth teams (1–8 people)
- **Secondary:** Product/Growth consultants running launch experiments

## 4) Jobs To Be Done
- “After a launch push, show me which UTM sources/campaigns produced meaningful conversions.”
- “Give me a cohort-level signal (basic retention/activation proxy) by first-touch source.”
- “Give me a dashboard I can trust without full enterprise analytics setup.”

## 5) MVP Goals (2 weeks)
Ship a usable v0 that supports:
- UTM-tagged event ingestion API
- Conversion funnel summary by source/campaign
- Cohort table (daily or weekly) by first-touch source
- Minimal auth + a single workspace/project model

## 6) Non-Goals (for this MVP)
- Multi-touch attribution modeling
- Advanced identity resolution across devices
- BI-grade custom query builder
- Complex role/permission systems
- Native ad platform spend syncs (Meta/Google/TikTok)

## 7) Core User Flow
1. Team adds tracking link params (`utm_source`, `utm_medium`, `utm_campaign`, optional content/term).
2. Product sends events to ingestion endpoint (`visit`, `signup`, `activated` or `purchase`).
3. Dashboard displays:
   - Traffic + conversion by source/campaign
   - Conversion rates by source
   - Cohort table by first-touch date + source
4. Team uses insights to reallocate launch effort.

## 8) Success Metrics / KPIs
### Product KPIs
- **Time-to-first-insight:** < 30 minutes from setup to first dashboard view
- **Data completeness:** ≥ 95% of conversion events include attributable source/campaign (or explicitly “direct/unknown”)
- **Dashboard freshness:** new events visible within 60 seconds (p95)

### Adoption KPIs (MVP validation)
- **Activation rate:** ≥ 60% of signups send at least 100 events within 48h
- **Weekly engagement:** ≥ 40% of activated workspaces return 2+ times/week

### Quality KPIs
- **Event ingestion success rate:** ≥ 99.5%
- **Attribution match rate:** ≥ 90% of conversions mapped to a first-touch source

## 9) Risks & Mitigations
- **Risk:** Dirty/missing UTM values
  - **Mitigation:** Validation + normalization + fallback buckets (`unknown`, `direct`)
- **Risk:** Event schema drift from clients
  - **Mitigation:** Strict schema version + reject/log malformed events
- **Risk:** Over-promising attribution accuracy
  - **Mitigation:** Explicitly label as first-touch MVP with known limitations

## 10) Launch Criteria (end of 2 weeks)
MVP is considered shipped when:
- Ingestion endpoint is stable and documented
- Dashboard shows source conversion and cohort view using real event stream
- At least 1 internal test project runs with live data for 3+ consecutive days
- KPI baseline report is generated
