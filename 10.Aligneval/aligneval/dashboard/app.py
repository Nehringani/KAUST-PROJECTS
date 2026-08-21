"""AlignEval — Streamlit dashboard entry point.

Run locally with:
    streamlit run dashboard/app.py

Six views wired through the sidebar:
    1. Overview
    2. DPO-Guard Pareto Frontier
    3. Defense Stack Comparison
    4. Temporal Tracking
    5. Unlearning Completeness
    6. Log New Result
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Make the sibling `database` package importable when Streamlit launches
# the script directly (Streamlit does not add the project root to sys.path).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db import (  # noqa: E402
    DEFAULT_DB_PATH,
    METRIC_TAXONOMY,
    PROJECTS,
    get_connection,
    log_result,
)

st.set_page_config(
    page_title="AlignEval — LLM Alignment Research Dashboard",
    page_icon="🛡️",
    layout="wide",
)


# ---------------------------------------------------------------------------
# Data access helpers (cached so the UI stays snappy on repeated interaction)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=5)
def load_experiments() -> pd.DataFrame:
    """Return every experiment row as a DataFrame with parsed timestamps."""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM experiments", conn)
    finally:
        conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    return df


@st.cache_data(ttl=5)
def load_unlearning() -> pd.DataFrame:
    """Return every unlearning heatmap cell as a DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM unlearning_retrieval", conn)
    finally:
        conn.close()
    return df


def refresh_caches() -> None:
    """Invalidate cached queries after a write."""
    load_experiments.clear()
    load_unlearning.clear()


# ---------------------------------------------------------------------------
# View 1 — Overview
# ---------------------------------------------------------------------------
def view_overview(df: pd.DataFrame) -> None:
    st.title("AlignEval — Overview")
    st.caption("Unified tracker for LLM alignment technique performance across the 10-project portfolio.")

    total_experiments = len(df)
    best_resistance = (
        df.loc[df["metric_name"] == "injection_resistance_rate", "metric_value"].max()
        if not df.empty else 0.0
    )
    projects_active = df["project"].nunique() if not df.empty else 0
    models_tested = df["model"].nunique() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total experiments", f"{total_experiments}")
    c2.metric("Best injection resistance", f"{(best_resistance or 0) * 100:.1f}%")
    c3.metric("Projects active", f"{projects_active}")
    c4.metric("Models tested", f"{models_tested}")

    st.subheader("Results timeline")
    if df.empty:
        st.info("No experiments yet. Seed dummy data or use the 'Log New Result' view.")
        return

    fig = px.scatter(
        df,
        x="timestamp",
        y="metric_value",
        color="project",
        hover_data=["model", "experiment_id", "metric_name", "beta", "defense_config"],
        labels={"timestamp": "Date", "metric_value": "Metric value (normalized)"},
    )
    fig.update_layout(height=460, legend_title_text="Project")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Latest result per project")
    latest = (
        df.sort_values("timestamp")
        .groupby("project", as_index=False)
        .tail(1)
        .sort_values("project")
    )
    st.dataframe(
        latest[["project", "model", "experiment_id", "metric_name", "metric_value", "timestamp"]],
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------------------------
# View 2 — DPO-Guard Pareto Frontier
# ---------------------------------------------------------------------------
def view_dpo_pareto(df: pd.DataFrame) -> None:
    st.title("DPO-Guard — Pareto Frontier")
    st.caption("Helpfulness retention vs. injection resistance across DPO beta values.")

    dpo = df[df["project"] == "dpo-guard"].copy()
    if dpo.empty:
        st.info("No DPO-Guard results yet. Log helpfulness_retention and injection_resistance_rate rows sharing an experiment_id.")
        return

    # Pivot: one row per experiment_id, columns = metric_name.
    wide = (
        dpo.pivot_table(
            index=["experiment_id", "beta", "model"],
            columns="metric_name",
            values="metric_value",
            aggfunc="last",
        )
        .reset_index()
    )
    needed = {"helpfulness_retention", "injection_resistance_rate"}
    if not needed.issubset(wide.columns):
        st.warning(f"Need both metrics per experiment: {sorted(needed)}. Currently have: {list(wide.columns)}")
        return

    wide = wide.dropna(subset=list(needed))
    if wide.empty:
        st.info("No experiment has both helpfulness_retention and injection_resistance_rate yet.")
        return

    # Compute Pareto frontier: maximize both axes.
    pts = wide.sort_values("helpfulness_retention", ascending=False).reset_index(drop=True)
    frontier: list[int] = []
    best_y = -1.0
    for i, row in pts.iterrows():
        if row["injection_resistance_rate"] > best_y:
            frontier.append(i)
            best_y = float(row["injection_resistance_rate"])
    frontier_df = pts.loc[frontier].sort_values("helpfulness_retention")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=wide["helpfulness_retention"],
        y=wide["injection_resistance_rate"],
        mode="markers+text",
        marker=dict(size=12, color="#4C78A8"),
        text=[f"β={b:.2f}" if pd.notna(b) else "" for b in wide["beta"]],
        textposition="top center",
        name="Experiments",
        hovertext=wide["experiment_id"],
    ))
    fig.add_trace(go.Scatter(
        x=frontier_df["helpfulness_retention"],
        y=frontier_df["injection_resistance_rate"],
        mode="lines+markers",
        line=dict(color="#E45756", width=2, dash="dash"),
        name="Pareto frontier",
    ))
    fig.update_layout(
        height=520,
        xaxis_title="Helpfulness retention",
        yaxis_title="Injection resistance rate",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Recommend the frontier point closest to the top-right corner.
    frontier_df = frontier_df.assign(
        distance=lambda d: ((1 - d["helpfulness_retention"]) ** 2
                            + (1 - d["injection_resistance_rate"]) ** 2) ** 0.5
    )
    rec = frontier_df.sort_values("distance").iloc[0]
    st.success(
        f"**Recommended β for SOC deployment: {rec['beta']:.2f}** — "
        f"helpfulness {rec['helpfulness_retention']:.2f}, "
        f"resistance {rec['injection_resistance_rate']:.2f} "
        f"({rec['experiment_id']})."
    )


# ---------------------------------------------------------------------------
# View 3 — Defense Stack Comparison
# ---------------------------------------------------------------------------
DEFENSE_ORDER = ["none", "promptshield", "dpo-guard", "both", "all-three"]


def view_defense_stack(df: pd.DataFrame) -> None:
    st.title("Defense Stack Comparison")
    st.caption("Attack success rate by defense configuration — lower is better.")

    d = df[df["metric_name"] == "attack_success_rate"].copy()
    if d.empty:
        st.info("No attack_success_rate results yet.")
        return

    projects = sorted(d["project"].dropna().unique().tolist())
    with st.container():
        col_a, col_b = st.columns(2)
        chosen_projects = col_a.multiselect("Filter by project (SOC context)", projects, default=projects)
        notes_filter = col_b.text_input("Filter notes contains (attack class)", value="")

    d = d[d["project"].isin(chosen_projects)]
    if notes_filter:
        d = d[d["notes"].fillna("").str.contains(notes_filter, case=False)]

    if d.empty:
        st.info("No rows match the current filters.")
        return

    agg = (
        d.groupby("defense_config", dropna=False)["metric_value"]
        .mean()
        .reset_index()
    )
    agg["defense_config"] = agg["defense_config"].fillna("none")
    agg["order"] = agg["defense_config"].apply(
        lambda x: DEFENSE_ORDER.index(x) if x in DEFENSE_ORDER else len(DEFENSE_ORDER)
    )
    agg = agg.sort_values("order")

    fig = px.bar(
        agg,
        x="defense_config",
        y="metric_value",
        text=agg["metric_value"].map(lambda v: f"{v*100:.0f}%"),
        labels={"defense_config": "Defense stack", "metric_value": "Attack success rate"},
        color="defense_config",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=480, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Defense-in-depth compounds: stacking PromptShield + DPO-Guard should sit well below either alone.")


# ---------------------------------------------------------------------------
# View 4 — Temporal Tracking
# ---------------------------------------------------------------------------
def view_temporal(df: pd.DataFrame) -> None:
    st.title("Temporal Tracking")
    st.caption("How each metric evolves across experiment iterations.")

    if df.empty:
        st.info("No data yet.")
        return

    metric = st.selectbox("Metric", METRIC_TAXONOMY, index=0)
    projects = sorted(df["project"].unique().tolist())
    chosen = st.multiselect("Projects", projects, default=projects)

    sub = df[(df["metric_name"] == metric) & (df["project"].isin(chosen))].copy()
    if sub.empty:
        st.info("No rows for this metric / project combination.")
        return
    sub = sub.sort_values("timestamp")

    fig = px.line(
        sub,
        x="timestamp",
        y="metric_value",
        color="project",
        markers=True,
        hover_data=["experiment_id", "model", "beta", "defense_config"],
        labels={"timestamp": "Date", "metric_value": metric},
    )
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# View 5 — Unlearning Completeness
# ---------------------------------------------------------------------------
def view_unlearning(unl: pd.DataFrame, df: pd.DataFrame) -> None:
    st.title("Unlearning Completeness")
    st.caption("Heatmap: knowledge target × retrieval vector. Higher = more leakage.")

    if unl.empty:
        st.info("No unlearning cells yet. Seed data or insert via database.log_unlearning_cell().")
        return

    exps = sorted(unl["experiment_id"].unique().tolist())
    chosen_exp = st.selectbox("Experiment", exps, index=len(exps) - 1)
    cells = unl[unl["experiment_id"] == chosen_exp]

    pivot = cells.pivot_table(
        index="knowledge_target",
        columns="retrieval_vector",
        values="retrieval_score",
        aggfunc="max",
    ).fillna(0)

    fig = px.imshow(
        pivot,
        color_continuous_scale="Inferno",
        zmin=0,
        zmax=3,
        aspect="auto",
        labels=dict(color="Retrieval score"),
    )
    fig.update_layout(height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Completeness per target")
    # Completeness = 1 - (max score / 3), summarised per target.
    completeness = (1 - pivot.max(axis=1) / 3).reset_index()
    completeness.columns = ["knowledge_target", "completeness"]
    bar = px.bar(
        completeness,
        x="knowledge_target",
        y="completeness",
        labels={"completeness": "Unlearning completeness"},
    )
    bar.update_layout(height=360, yaxis_tickformat=".0%")
    st.plotly_chart(bar, use_container_width=True)

    # Also show any aggregate unlearning_completeness rows from experiments table.
    scalar = df[(df["metric_name"] == "unlearning_completeness")
                & (df["experiment_id"] == chosen_exp)]
    if not scalar.empty:
        st.info(f"Reported unlearning_completeness for {chosen_exp}: "
                f"{scalar['metric_value'].iloc[-1]:.2%}")


# ---------------------------------------------------------------------------
# View 6 — Log New Result
# ---------------------------------------------------------------------------
def view_log_form() -> None:
    st.title("Log New Result")
    st.caption("Direct data-entry into the SQLite results database.")

    with st.form("log_result_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        project = c1.selectbox("Project", PROJECTS)
        model = c2.text_input("Model", placeholder="e.g. phi-2, mistral-7b, claude-haiku")

        c3, c4 = st.columns(2)
        experiment_id = c3.text_input("Experiment ID", placeholder="EXP-DPOGUARD-007")
        metric_name = c4.selectbox("Metric", METRIC_TAXONOMY)

        c5, c6 = st.columns(2)
        metric_value = c5.number_input("Metric value (0.0–1.0)", min_value=0.0, max_value=1.0, value=0.5, step=0.01)
        beta = c6.number_input("Beta (DPO only, optional)", min_value=0.0, max_value=10.0, value=0.0, step=0.05)

        defense_config = st.selectbox(
            "Defense config",
            ["", "none", "promptshield", "dpo-guard", "both", "all-three"],
        )
        notes = st.text_area("Notes", placeholder="Free-form context — attack class, dataset slice, etc.")

        submitted = st.form_submit_button("Log result")

    if submitted:
        if not model or not experiment_id:
            st.error("Model and Experiment ID are required.")
            return
        conn = get_connection()
        try:
            row_id = log_result(
                conn,
                project=project,
                model=model.strip(),
                experiment_id=experiment_id.strip(),
                metric_name=metric_name,
                metric_value=float(metric_value),
                beta=float(beta) if beta > 0 else None,
                defense_config=defense_config or None,
                notes=notes.strip() or None,
            )
        finally:
            conn.close()
        refresh_caches()
        st.success(
            f"Logged row #{row_id}: {project}/{model} · {metric_name}={metric_value:.3f} "
            f"@ {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
        )


# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
VIEWS = {
    "Overview": "overview",
    "DPO-Guard Pareto": "pareto",
    "Defense Stack": "defense",
    "Temporal Tracking": "temporal",
    "Unlearning Completeness": "unlearning",
    "Log New Result": "log",
}


def main() -> None:
    st.sidebar.title("AlignEval")
    st.sidebar.caption("LLM alignment research dashboard")
    choice = st.sidebar.radio("Views", list(VIEWS.keys()), index=0)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"DB: `{os.path.relpath(DEFAULT_DB_PATH, PROJECT_ROOT)}`")
    st.sidebar.caption("Nehrin Gani · CyberSaR Laboratory")

    df = load_experiments()
    unl = load_unlearning()

    key = VIEWS[choice]
    if key == "overview":
        view_overview(df)
    elif key == "pareto":
        view_dpo_pareto(df)
    elif key == "defense":
        view_defense_stack(df)
    elif key == "temporal":
        view_temporal(df)
    elif key == "unlearning":
        view_unlearning(unl, df)
    elif key == "log":
        view_log_form()


if __name__ == "__main__":
    main()
