"""Streamlit dashboard for exploring SOC-RedTeam results."""
from __future__ import annotations

import os
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

DEFAULT_DB = os.environ.get("SOC_REDTEAM_DB", "database/results.db")

st.set_page_config(page_title="SOC-RedTeam Dashboard", layout="wide")
st.title("SOC-RedTeam — Attack Success Dashboard")

db_path = st.sidebar.text_input("SQLite database path", DEFAULT_DB)
if not os.path.exists(db_path):
    st.warning(f"Database not found at `{db_path}`. Run `python -m src.runner` first.")
    st.stop()


@st.cache_data(ttl=5)
def load(path: str) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        return pd.read_sql_query("SELECT * FROM experiments", conn)


df = load(db_path)
if df.empty:
    st.info("No experiments recorded yet.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Total attacks", len(df))
col2.metric("Overall success rate", f"{df['attack_succeeded'].mean() * 100:.1f}%")
col3.metric("Blocked by defense", int(df["defense_blocked"].sum()))

st.subheader("Success rate by defense configuration")
by_def = (
    df.groupby("defense_applied")["attack_succeeded"]
      .agg(["mean", "count"])
      .reset_index()
      .rename(columns={"mean": "success_rate", "count": "total_attacks"})
)
st.plotly_chart(
    px.bar(by_def, x="defense_applied", y="success_rate", text="total_attacks"),
    use_container_width=True,
)

st.subheader("Success rate by attack module × defense")
pivot = (
    df.pivot_table(
        index="attack_module",
        columns="defense_applied",
        values="attack_succeeded",
        aggfunc="mean",
    ).fillna(0.0)
)
st.dataframe(pivot.style.format("{:.2%}"), use_container_width=True)

st.subheader("Success rate by SOC context × defense")
pivot_ctx = (
    df.pivot_table(
        index="soc_context",
        columns="defense_applied",
        values="attack_succeeded",
        aggfunc="mean",
    ).fillna(0.0)
)
st.dataframe(pivot_ctx.style.format("{:.2%}"), use_container_width=True)

st.subheader("Raw experiments")
st.dataframe(df, use_container_width=True, height=400)
