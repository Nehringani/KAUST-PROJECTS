"""Streamlit analyst dashboard for ThreatLens (3-column layout)."""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running via `streamlit run dashboard/app.py` without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from src.threatlens.feeds import fetch_cisa_alerts, fetch_urlhaus, FeedItem
from src.threatlens.pipeline import run_pipeline
from src.threatlens.simulated_feeds import INJECTED_FEEDS

st.set_page_config(page_title="ThreatLens", layout="wide")
st.title("ThreatLens — Injection-Resilient Threat Intelligence")

# --- Sidebar controls ------------------------------------------------------
with st.sidebar:
    st.header("Ingestion")
    source = st.selectbox("Source", ["Simulated injected samples (20)", "CISA RSS", "abuse.ch URLhaus"])
    fetch_clicked = st.button("Fetch latest items", use_container_width=True)
    st.markdown("---")
    st.header("Defense layers")
    l1 = st.checkbox("Layer 1 — Preprocessing", value=True)
    l2 = st.checkbox("Layer 2 — PromptShield", value=True)
    l3 = st.checkbox("Layer 3 — Schema validation", value=True)


@st.cache_data(show_spinner=False, ttl=300)
def _get_items(source_name: str):
    if source_name.startswith("Simulated"):
        return INJECTED_FEEDS
    if source_name == "CISA RSS":
        return fetch_cisa_alerts(limit=15)
    return fetch_urlhaus(limit=15)


items = _get_items(source) if fetch_clicked or source.startswith("Simulated") else []

# Run pipeline on all items ------------------------------------------------
results = [run_pipeline(it, use_layer1=l1, use_layer2=l2, use_layer3=l3) for it in items]

# --- 3 Columns -------------------------------------------------------------
col1, col2, col3 = st.columns(3)

# COLUMN 1 — Feed Ingestion
with col1:
    st.subheader("Feed Ingestion")
    if not items:
        st.info("Choose a source and click **Fetch latest items**.")
    else:
        df = pd.DataFrame([
            {
                "Title": (it.title or "")[:70],
                "Source": it.source,
                "L1": r.layer1_score if r.layer1_score is not None else "-",
                "L2": "BLOCK" if r.layer2_detected else ("ok" if r.layer2_detected is False else "-"),
                "Flagged": "yes" if r.injection_flagged else "no",
            }
            for it, r in zip(items, results)
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

# COLUMN 2 — Analysis results
with col2:
    st.subheader("Analysis Results")
    shown = 0
    for it, r in zip(items, results):
        if r.quarantined or r.schema_valid is False or not r.synthesized:
            continue
        level = str(r.synthesized.get("threat_level", "unknown")).lower()
        color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "⚪")
        with st.expander(f"{color} {it.title[:80]}"):
            st.write(r.synthesized.get("summary", ""))
            st.markdown(f"**Threat level:** {level}")
            st.markdown(f"**IOC count:** {r.synthesized.get('ioc_count')}")
            ttps = r.synthesized.get("mitre_ttps") or []
            if ttps:
                st.markdown("**MITRE ATT&CK TTPs:** " + ", ".join(ttps))
        shown += 1
    if items and shown == 0:
        st.warning("No clean reports — every item was blocked by the defense layers.")

# COLUMN 3 — Security status
with col3:
    st.subheader("Security Status")
    blocked_l2 = sum(1 for r in results if r.quarantined)
    blocked_l3 = sum(1 for r in results if r.schema_valid is False)
    flagged_l1 = sum(1 for r in results if (r.layer1_score or 0) >= 1)
    total = len(results)
    m1, m2, m3 = st.columns(3)
    m1.metric("L1 flagged", flagged_l1)
    m2.metric("L2 blocked", blocked_l2)
    m3.metric("L3 rejected", blocked_l3)
    st.markdown("---")
    st.markdown("**Injection alert log**")
    alerts = [
        {"Title": r.item_title[:60],
         "Layer": ("L2" if r.quarantined else ("L3" if r.schema_valid is False else "L1")),
         "Confidence": r.layer2_confidence or "-",
         "Class": r.layer2_class or "-"}
        for r in results if r.injection_flagged
    ]
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)
    else:
        st.success("No injection alerts.")

st.markdown("---")
st.caption("Run `python -m src.threatlens.experiment` to measure marginal contribution of each layer.")
