"""
ParamRisk — Streamlit Interactive Web Application
Run via: streamlit run app.py
"""

import streamlit as st
import math
import random
from engine.extreme_value import ExtremeValueDistribution
from engine.parametric_contract import ParametricContract
from engine.monte_carlo import MonteCarloPricer

st.set_page_config(
    page_title="ParamRisk — Parametric Insurance Pricing Engine",
    page_icon="🌪️",
    layout="wide"
)

st.title("🌪️ ParamRisk — Climate Insurtech & Actuarial Pricing Engine")
st.markdown("Interactive quantitative simulation platform for parametric disaster risk financing.")

# Sidebar Controls
st.sidebar.header("⚙️ Contract Configuration")

peril = st.sidebar.selectbox("Peril Type", ["Drought Deficit Index", "Excess Heatwave Index"])
sum_insured = st.sidebar.number_input("Maximum Sum Insured (INR)", min_value=1000, max_value=100000, value=20000, step=1000)

if peril == "Drought Deficit Index":
    strike = st.sidebar.slider("Strike Trigger (mm Deficit)", 50, 200, 120, 5)
    exit_thresh = st.sidebar.slider("Exit Threshold (mm Deficit)", 150, 350, 250, 5)
    direction = "deficit"
else:
    strike = st.sidebar.slider("Strike Trigger (°C Max Temp)", 40, 48, 44, 1)
    exit_thresh = st.sidebar.slider("Exit Threshold (°C Max Temp)", 45, 52, 48, 1)
    direction = "excess"

risk_margin_pct = st.sidebar.slider("Solvency Risk Margin (% of StdDev)", 5, 30, 15, 1)
n_simulations = st.sidebar.selectbox("Monte Carlo Iterations", [5000, 10000, 25000], index=1)

# Fit EVT model
# Long-term Gujarat empirical parameters: Mean ~85mm deficit, StdDev ~42mm
evt = ExtremeValueDistribution(dist_type="gumbel")
# Synthetic sample for demo
sample = [random.gauss(85, 42) for _ in range(30)]
evt.fit_moments(sample)

contract = ParametricContract(
    strike=strike,
    exit_threshold=exit_thresh,
    max_payout=sum_insured,
    direction=direction
)

pricer = MonteCarloPricer(evt_model=evt, contract=contract, n_iterations=n_simulations)
results = pricer.run_simulation(risk_margin_factor=risk_margin_pct / 100.0, expense_loading=0.10)

# Display Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pure Premium (Expected Loss)", f"₹{results['pure_premium']:,.2f}")
col2.metric("Burn Rate", f"{results['burn_rate_pct']:.2f}%")
col3.metric("Tail VaR (99% / Solvency)", f"₹{results['tvar_99']:,.2f}")
col4.metric("Commercial Gross Premium", f"₹{results['commercial_premium']:,.2f}")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Parametric Payout Curve")
    st.markdown(f"**Strike**: {strike} | **Exit**: {exit_thresh} | **Max Payout**: ₹{sum_insured:,}")
    st.info("Linear tick payout function: Payout increases proportionally between Strike and Exit bounds.")

with col_right:
    st.subheader("🔬 Return Period Benchmarks")
    return_periods = evt.estimate_return_periods([2, 5, 10, 25, 50, 100])
    st.dataframe(return_periods, use_container_width=True)

st.success("Repository maintained by Nilesh Mori (DA-IICT Gandhinagar) • Open Source Under MIT License")
