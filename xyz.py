# app.py
"""
Conservative Investment Allocation — Streamlit App (stable)
Save this file as app.py and run:
    pip install streamlit pandas plotly
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Conservative Portfolio", layout="wide")

# ---------- Default dataset ----------
def default_portfolio_df():
    data = {
        "Asset": [
            "Fixed Deposits (FD)",
            "Public Provident Fund (PPF)",
            "Debt Mutual Funds",
            "Government Bonds (G-Secs)",
            "Senior Citizens Savings Scheme (SCSS)",
        ],
        "Risk": ["Very Low", "Very Low", "Low", "Very Low", "Very Low"],
        "Reward": ["5-7", "7.1 (current)", "6-8", "6-7", "8.2 (current)"],
        "Time of Investment": ["1-5 years", "15 years", "3-5 years", "5+ years", "5 years"],
        "Allocation (%)": [30.0, 20.0, 20.0, 20.0, 10.0],
        "Source": ["RBI, SBI", "India Post", "AMFI", "RBI", "India Post"],
        "Reasons": [
            "Provides stable returns in the 5–7% range. Perfect for short to medium-term goals (1–5 years). No market volatility; liquidity with penalty for early withdrawal.",
            "Government-backed; one of India's safest long-term instruments. EEE tax treatment; builds retirement corpus.",
            "Suitable for low-risk investors seeking better post-tax returns than FD. Offers liquidity, diversification, and indexation benefits.",
            "Considered risk-free (backed by Government of India). Good for wealth preservation and long-term stability.",
            "Designed for senior citizens with one of the highest safe rates (currently 8.2%). Quarterly payouts provide regular income.",
        ],
    }
    return pd.DataFrame(data)

# ---------- Helpers ----------
def sum_allocations(df):
    return float(pd.to_numeric(df["Allocation (%)"], errors="coerce").fillna(0).sum())

def is_allocation_ok(df, tol=1e-6):
    return abs(sum_allocations(df) - 100.0) <= tol

def normalize_allocations(df):
    df = df.copy()
    vals = pd.to_numeric(df["Allocation (%)"], errors="coerce").fillna(0.0)
    total = vals.sum()
    if total == 0:
        n = len(vals)
        normalized = pd.Series([100.0 / n] * n, index=df.index)
    else:
        normalized = (vals / total) * 100.0
    rounded = normalized.round(2)
    residue = 100.0 - rounded.sum()
    if abs(residue) > 1e-9:
        # add residue to largest allocation (minimize distortion)
        if rounded.sum() != 0:
            idx = rounded.idxmax()
        else:
            idx = rounded.index[0]
        rounded.at[idx] = rounded.at[idx] + residue
    df["Allocation (%)"] = rounded
    return df

def df_to_csv_bytes(df):
    buf = StringIO()
    df.to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")

# ---------- App state ----------
if "portfolio_df" not in st.session_state:
    st.session_state.portfolio_df = default_portfolio_df()

# Copy for local edits
df = st.session_state.portfolio_df.copy()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Controls")
    show_reasons = st.checkbox("Show Source & Reasons", value=True)
    if st.button("Reset to default"):
        st.session_state.portfolio_df = default_portfolio_df()
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("Presets")
    preset = st.selectbox("Choose a preset", ["— none —", "Default Conservative", "Ultra-safe (more FD/G-Secs)", "Income-focused (more PPF/SCSS)"])
    if st.button("Apply preset"):
        if preset == "Default Conservative":
            st.session_state.portfolio_df["Allocation (%)"] = [30.0, 20.0, 20.0, 20.0, 10.0]
        elif preset == "Ultra-safe (more FD/G-Secs)":
            st.session_state.portfolio_df["Allocation (%)"] = [40.0, 15.0, 10.0, 25.0, 10.0]
        elif preset == "Income-focused (more PPF/SCSS)":
            st.session_state.portfolio_df["Allocation (%)"] = [20.0, 30.0, 10.0, 20.0, 20.0]
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("Tip: Edit allocations below and click **Save changes**. If the sum ≠ 100%, use **Normalize**.")

# ---------- Editable table (stable) ----------
st.title("Conservative Investment Allocation")
st.markdown("Edit `Allocation (%)` values below. Only numeric allocations are editable to keep the app stable across Streamlit versions.")

cols = st.columns([3, 1.2, 1.2, 1.2, 1.4])  # header layout
cols[0].markdown("**Asset**")
cols[1].markdown("**Reward**")
cols[2].markdown("**Time**")
cols[3].markdown("**Allocation (%)**")
cols[4].markdown("**Source**")

new_allocs = []
for i, row in df.iterrows():
    c_asset, c_reward, c_time, c_alloc, c_source = st.columns([3, 1.2, 1.2, 1.2, 1.4])
    c_asset.write(row["Asset"])
    c_reward.write(row["Reward"])
    c_time.write(row["Time of Investment"])
    # numeric input for allocation
    key = f"alloc_{i}"
    current = float(pd.to_numeric(row["Allocation (%)"], errors="coerce").fillna(0.0))
    value = c_alloc.number_input(label="", min_value=0.0, max_value=100.0, value=current, step=0.5, format="%.2f", key=key)
    new_allocs.append(float(value))
    c_source.write(row["Source"])
    if show_reasons:
        st.write(f"**Reasons:** {row['Reasons']}")

# Update with new allocations
df["Allocation (%)"] = new_allocs

# ---------- Actions ----------
st.markdown("---")
a1, a2, a3 = st.columns([1,1,1])
with a1:
    total = sum_allocations(df)
    if is_allocation_ok(df):
        st.success(f"Total allocation = {total:.2f}% (OK)")
    else:
        st.error(f"Total allocation = {total:.2f}% — not 100%")
with a2:
    if st.button("Normalize allocations → 100%"):
        df = normalize_allocations(df)
        st.session_state.portfolio_df = df
        st.success("Allocations normalized to sum 100%")
        st.experimental_rerun()
with a3:
    if st.button("Save changes"):
        st.session_state.portfolio_df["Allocation (%)"] = df["Allocation (%)"].values
        st.success("Saved allocation changes in session")

# Persist current view
st.session_state.portfolio_df = df.copy()

# ---------- Visualizations ----------
st.subheader("Visualizations")
chart_df = df.copy()
chart_df["Allocation (%)"] = pd.to_numeric(chart_df["Allocation (%)"], errors="coerce").fillna(0.0)

left, right = st.columns(2)
with left:
    if chart_df["Allocation (%)"].sum() > 0:
        fig = px.pie(chart_df, names="Asset", values="Allocation (%)", title="Portfolio Allocation (%)", hole=0.35)
        fig.update_traces(textinfo="percent+label", textposition="inside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Set allocations > 0 to view the pie chart.")
with right:
    fig2 = px.bar(chart_df.sort_values("Allocation (%)", ascending=True), x="Allocation (%)", y="Asset", orientation="h", text="Allocation (%)", title="Allocation by Asset")
    fig2.update_layout(xaxis_title="Allocation (%)")
    st.plotly_chart(fig2, use_container_width=True)

# ---------- Full table preview & export ----------
st.subheader("Full Portfolio Details")
st.dataframe(df, use_container_width=True)

st.subheader("Export")
csv_bytes = df_to_csv_bytes(df)
st.download_button("Download portfolio as CSV", data=csv_bytes, file_name="conservative_portfolio.csv", mime="text/csv")

st.markdown("---")
st.markdown(
    """
    **Notes**
    - This app is a demo (not investment advice). 
    - If you'd like editable text columns too (Asset/Source/Reasons), tell me your Streamlit version and I will produce a version that uses an in-app form for editing those columns.
    """
)
