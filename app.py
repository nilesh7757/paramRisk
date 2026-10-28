"""
ParamRisk — Streamlit Interactive Web Application
Run via: streamlit run app.py
"""

import streamlit as st
import math
import random
from engine.extreme_value import GumbelDistribution
from engine.parametric_contract import ParametricContract, TriggerDirection
from engine.monte_carlo import MonteCarloPricingEngine

st.set_page_config(
    page_title="ParamRisk — Parametric Insurance Pricing Engine",
    page_icon="🌪️",
    layout="wide"
)

st.title("🌪️ ParamRisk — Climate Insurtech & Actuarial Pricing Engine")
st.markdown("Interactive quantitative simulation platform for parametric disaster risk financing.")

# Sidebar Controls
st.sidebar.header("⚙️ Contract Configuration")

peril = st.sidebar.selectbox("Peril Type", ["Drought Rainfall Deficit", "Extreme Heatwave Index"])
sum_insured = st.sidebar.number_input("Maximum Sum Insured (INR)", min_value=1000, max_value=100000, value=20000, step=1000)

if peril == "Drought Rainfall Deficit":
    strike = st.sidebar.slider("Strike Trigger (mm Rainfall)", 60, 200, 120, 5)
    exit_thresh = st.sidebar.slider("Exit Threshold (mm Rainfall)", 20, strike - 10, 50, 5)
    direction = TriggerDirection.DEFICIT
    index_name = "Cumulative Rainfall (mm)"
    contract_name = "Gujarat Kharif Drought Protection"
    # Gujarat historical rainfall distribution: Mean ~140mm, Std ~55mm
    sample = [random.gauss(140, 55) for _ in range(40)]
else:
    strike = st.sidebar.slider("Strike Trigger (°C Max Temp)", 40, 48, 44, 1)
    exit_thresh = st.sidebar.slider("Exit Threshold (°C Max Temp)", strike + 1, 52, 48, 1)
    direction = TriggerDirection.EXCESS
    index_name = "Daily Max Temperature (°C)"
    contract_name = "Urban Heatwave Worker Protection"
    # Gujarat summer peak temp distribution: Mean ~41.5°C, Std ~2.5°C
    sample = [random.gauss(41.5, 2.5) for _ in range(40)]

n_simulations = st.sidebar.selectbox("Monte Carlo Iterations", [5000, 10000, 25000], index=1)

# Fit EVT model
evt = GumbelDistribution.fit_moments(sample)

contract = ParametricContract(
    contract_name=contract_name,
    index_name=index_name,
    strike=float(strike),
    exit_val=float(exit_thresh),
    max_payout=float(sum_insured),
    direction=direction
)

pricer = MonteCarloPricingEngine(contract=contract, distribution=evt)
results = pricer.run_simulation(num_iterations=n_simulations)

# Display Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pure Premium (Expected Loss)", f"₹{results['pure_premium']:,.2f}")
col2.metric("Burn Rate", f"{results['burn_rate_pct']:.2f}%")
col3.metric("Tail VaR (TVaR 99%)", f"₹{results['tvar_99_expected_shortfall']:,.2f}")
col4.metric("Commercial Gross Premium", f"₹{results['suggested_commercial_premium']:,.2f}")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Contract Structure")
    st.write(f"**Contract Name:** {contract.contract_name}")
    st.write(f"**Index Monitored:** {contract.index_name}")
    st.write(f"**Direction:** {contract.direction.value}")
    st.write(f"**Strike Trigger:** {strike} (Payout starts)")
    st.write(f"**Exit Threshold:** {exit_thresh} (100% Payout capped at ₹{sum_insured:,})")
    st.write(f"**Claim Frequency:** {results['claim_frequency_pct']}% of seasons")
    st.write(f"**Value-at-Risk (VaR 99%):** ₹{results['var_99']:,.2f}")

with col_right:
    st.subheader("🔬 Extreme Value Theory (EVT) Return Periods")
    return_periods = evt.generate_return_period_table([2.0, 5.0, 10.0, 25.0, 50.0, 100.0])
    st.dataframe(return_periods, width='stretch')

st.success("ParamRisk Engine • Developed by Nilesh Mori (DA-IICT Gandhinagar) • Open Source Under MIT License")
