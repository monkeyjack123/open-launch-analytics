"""Core utilities for Open Launch Analytics MVP."""

from .attribution import build_first_touch_attribution, build_last_touch_attribution
from .auth import ApiKeyManager, validate_api_key, validate_api_key_hash
from .cohorts import build_signup_cohorts
from .events import normalize_event, validate_event
from .ingest import ingest_batch, ingest_event, measure_ingest_throughput
from .metrics import (
    aggregate_conversion_metrics,
    backfill_conversion_metrics,
    build_dashboard_filter_options,
    build_funnel_breakdown,
    build_funnel_timeseries,
    resolve_date_range,
    summarize_campaign_efficiency,
    summarize_funnel,
)
from .quality import (
    build_attribution_completeness_report,
    build_daily_quality_trend,
    build_data_quality_report,
    build_health_status,
    build_ingestion_slo_report,
    build_observability_snapshot,
)
from .sample_data import build_sample_events, sample_events_to_ndjson

__all__ = [
    "normalize_event",
    "validate_event",
    "ingest_event",
    "ingest_batch",
    "measure_ingest_throughput",
    "build_first_touch_attribution",
    "build_last_touch_attribution",
    "aggregate_conversion_metrics",
    "backfill_conversion_metrics",
    "summarize_funnel",
    "build_funnel_breakdown",
    "build_funnel_timeseries",
    "build_dashboard_filter_options",
    "resolve_date_range",
    "summarize_campaign_efficiency",
    "build_signup_cohorts",
    "validate_api_key",
    "validate_api_key_hash",
    "ApiKeyManager",
    "build_data_quality_report",
    "build_attribution_completeness_report",
    "build_daily_quality_trend",
    "build_ingestion_slo_report",
    "build_health_status",
    "build_observability_snapshot",
    "build_sample_events",
    "sample_events_to_ndjson",
]
