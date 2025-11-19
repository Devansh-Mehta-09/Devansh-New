import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration ---
# Set the page configuration for a better look and feel
st.set_page_config(
    page_title="Risk-Averse Investment Portfolio Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Preparation ---

# Data directly from the provided table
data = {
    'Asset': [
        'Fixed Deposits (FD)',
        'Public Provident Fund (PPF)',
        'Debt Mutual Funds',
        'Government Bonds (G-Secs)',
        'Senior Citizens Savings Scheme (SCSS)'
    ],
    'Risk': [
        'Very Low',
        'Very Low',
        'Low',
        'Very Low',
        'Very Low'
    ],
    'Reward Range (%)': [
        '5-7',
        '7.1 (current)',
        '6-8',
        '6-7',
        '8.2 (current)'
    ],
    'Time of Investment': [
        '2-5 years',
        '15 years',
        '3-5 years',
        '5+ years',
        '5 years'
    ],
    'Allocation (%)': [30, 20, 20, 20, 10],
    'Source': [
        'RBI, SBI',
        'India Post',
        'AMFI',
        'RBI',
        'India Post'
    ],
    'Reasons': [
        'Provides stable returns in the 5–7% range, perfect for short to medium-term goals in the next 1–5 years. No market volatility ideal for risk-averse investors. Liquidity available with penalty, suitable for emergency needs.',
        'Government-backed, making it one of India\'s safest long-term instruments. EBT (Exempt-Exempt-Exempt) status: interest tax-free, maturity tax-free. Helps in building a retirement corpus.',
        'Suitable for low-risk investors seeking better post-tax returns than FD. Provides liquidity, diversification, and indexation benefits for long-term investors.',
        'Considered risk-free, backed by Government of India. Safe for wealth preservation with long-term stability.',
        'Designed specifically for senior citizens with the highest safe interest rate (currently 8.2%). Quarterly interest payout provides regular income.'
    ]
}

df = pd.DataFrame(data)

# --- Streamlit Application Layout ---

st.title("🛡️ Risk-Averse Fixed-Income Portfolio")
st.markdown(
    """
    This dashboard visualizes the proposed allocation strategy focusing on capital preservation and stable,
    low-risk returns, primarily through government-backed and fixed-income instruments.
    """
)

st.subheader("1. Portfolio Asset Breakdown")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Allocation (%)": st.column_config.ProgressColumn(
            "Allocation (%)",
            help="Percentage of total capital allocated to this asset.",
            format="%d%%",
            min_value=0,
            max_value=100,
        )
    }
)

# --- Visualizations ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("2. Capital Allocation Distribution")
    
    # Pie chart using Plotly for allocation
    fig_pie = px.pie(
        df,
        values='Allocation (%)',
        names='Asset',
        title='Portfolio Allocation by Asset Class',
        hole=0.3  # Creates a donut chart
    )
    # Customize the chart appearance
    fig_pie.update_traces(
        textinfo='percent+label',
        marker=dict(line=dict(color='#000000', width=0.5)),
        hoverinfo='label+percent+value'
    )
    fig_pie.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide',
        legend_title="Asset Class",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("3. Allocation vs. Investment Horizon")
    
    # Since Time of Investment is non-numeric, we will map it to a category
    # For a simple visualization, we can show allocation by risk level as well.
    risk_summary = df.groupby('Risk')['Allocation (%)'].sum().reset_index()
    
    # Bar chart showing Allocation based on Risk
    fig_bar = px.bar(
        risk_summary,
        x='Risk',
        y='Allocation (%)',
        title='Total Allocation by Risk Level',
        color='Risk',
        color_discrete_map={'Very Low': '#1f77b4', 'Low': '#ff7f0e'} # Set custom colors
    )
    
    # Add labels and customize
    fig_bar.update_traces(marker_line_width=1.5, marker_line_color='black')
    fig_bar.update_layout(
        xaxis_title="Risk Category",
        yaxis_title="Total Allocation (%)",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
st.subheader("4. Detailed Investment Rationale")
st.info("Hover over the cards below to see the specific reasoning for the asset choice.")

# Display reasons in expandable/interactive cards
for index, row in df.iterrows():
    with st.expander(f"**{row['Asset']}** - {row['Allocation (%)']}% Allocation"):
        st.markdown(f"**Risk:** {row['Risk']}")
        st.markdown(f"**Reward Range:** {row['Reward Range (%)']} (Expected annual return)")
        st.markdown(f"**Time Horizon:** {row['Time of Investment']}")
        st.markdown(f"**Source/Authority:** {row['Source']}")
        st.markdown("---")
        st.markdown(f"**Investment Thesis:** {row['Reasons']}")


# --- Footer ---
st.markdown("---")
st.caption("Disclaimer: This is a sample portfolio visualization based on user-provided data and should not be considered professional financial advice.")
