#!/usr/bin/env python3
"""
Parametric Climate Risk & Actuarial Pricing Engine
Main Executable Driver

Demonstrates:
1. Historical Climate Data Ingestion (Gujarat Agricultural Districts)
2. Extreme Value Theory (EVT) Gumbel Distribution Fitting
3. Return Period Analysis (1-in-10, 1-in-25, 1-in-50 year events)
4. Parametric Insurance Trigger Calibration (Drought & Heatwave)
5. Monte Carlo Stochastic Simulation (10,000 runs)
6. Actuarial Capital & Solvency Pricing (Pure Premium, VaR 99%, TVaR)
"""

import csv
import json
from engine.extreme_value import GumbelDistribution
from engine.parametric_contract import ParametricContract, TriggerDirection
from engine.monte_carlo import MonteCarloPricingEngine

def print_banner(title: str):
    print("\n" + "=" * 78)
    print(f"  {title.upper()}")
    print("=" * 78)

def load_climate_data(filepath: str = "data/historical_climate_data.csv"):
    with open(filepath, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def run_pipeline():
    print_banner("InRisk Labs Parametric Climate Risk Simulation Engine")
    print("Author: Nilesh Mori (DA-IICT Gandhinagar • Minor in Computational Science)")
    print("Stack: Python EVT • Gumbel Modeling • Monte Carlo Stochastic Simulation")

    # 1. Ingestion
    records = load_climate_data()
    print(f"\n[1] Ingested {len(records)} historical climate records (1995-2025).")

    # Extract sample metrics for Porbandar / Saurashtra Region
    porbandar_rainfalls = [
        float(r["monsoon_sowing_rainfall_mm"])
        for r in records if r["district"] == "Porbandar"
    ]
    # For drought deficit modeling, we model deficit: (Target 400mm - Rainfall)
    rain_deficits = [max(0.0, 400.0 - r) for r in porbandar_rainfalls]

    heatwave_temps = [
        float(r["max_summer_temp_c"])
        for r in records if r["district"] == "Ahmedabad"
    ]

    # 2. Extreme Value Theory Fitting
    print_banner("Step 1: Extreme Value Theory (EVT) Parameter Estimation")
    drought_gumbel = GumbelDistribution.fit_moments(rain_deficits)
    print(f"• Saurashtra Rainfall Deficit Gumbel Parameters:")
    print(f"  Location (mu): {drought_gumbel.mu:.2f} mm | Scale (beta): {drought_gumbel.beta:.2f} mm")

    heat_gumbel = GumbelDistribution.fit_moments(heatwave_temps)
    print(f"• Ahmedabad Max Summer Temperature Gumbel Parameters:")
    print(f"  Location (mu): {heat_gumbel.mu:.2f} °C | Scale (beta): {heat_gumbel.beta:.2f} °C")

    # 3. Return Period Analysis
    print_banner("Step 2: Actuarial Climate Return Period Table (Ahmedabad Heatwave)")
    print(f"{'Return Period (Years)':<24} | {'Exceedance Prob':<18} | {'Design Max Temp (°C)':<22}")
    print("-" * 72)
    for row in heat_gumbel.generate_return_period_table([2, 5, 10, 25, 50, 100]):
        print(f"{row['return_period_years']:<24} | {row['annual_exceedance_prob']:<18.4f} | {row['threshold_value']:<22.2f}")

    # 4. Parametric Insurance Contracts
    print_banner("Step 3: Parametric Contract Formulation")

    # Contract A: Drought
    drought_contract = ParametricContract(
        contract_name="Saurashtra Groundnut Parametric Drought Shield",
        index_name="Cumulative Monsoon Sowing Rainfall (mm)",
        strike=140.0,       # Payout begins when rainfall drops below 140mm
        exit_val=60.0,      # Full payout when rainfall collapses below 60mm
        max_payout=35000.0, # ₹35,000 / hectare
        direction=TriggerDirection.DEFICIT
    )
    print(f"Contract 1: {drought_contract.contract_name}")
    print(f"• Strike Threshold: {drought_contract.strike} mm | Exit Threshold: {drought_contract.exit_val} mm")
    print(f"• Maximum Sum Insured: ₹{drought_contract.max_payout:,.2f} / hectare")

    # Contract B: Heatwave
    heat_contract = ParametricContract(
        contract_name="Ahmedabad Urban Daily-Wage Heatwave Shield",
        index_name="Maximum Ambient Temperature (°C)",
        strike=44.0,        # Payout begins when temp hits 44.0°C
        exit_val=47.5,      # 100% max payout at 47.5°C extreme
        max_payout=15000.0, # ₹15,000 / beneficiary
        direction=TriggerDirection.EXCESS
    )
    print(f"\nContract 2: {heat_contract.contract_name}")
    print(f"• Strike Threshold: {heat_contract.strike} °C | Exit Threshold: {heat_contract.exit_val} °C")
    print(f"• Maximum Sum Insured: ₹{heat_contract.max_payout:,.2f} / beneficiary")

    # 5. Monte Carlo Actuarial Pricing Simulation
    print_banner("Step 4: Monte Carlo Actuarial Pricing (10,000 Stochastic Iterations)")
    mc_engine = MonteCarloPricingEngine(heat_contract, heat_gumbel)
    results = mc_engine.run_simulation(num_iterations=10000, random_seed=42)

    print(f"Contract Evaluated: {results['contract_name']}")
    print(f"• Total Iterations       : {results['iterations']:,}")
    print(f"• Trigger Claim Frequency: {results['claim_frequency_pct']:.2f}% of seasons")
    print(f"• Pure Premium (Expected): ₹{results['pure_premium']:,.2f} ({results['burn_rate_pct']:.2f}% Burn Rate)")
    print(f"• Standard Deviation     : ₹{results['standard_deviation']:,.2f}")
    print(f"• Value-at-Risk (VaR 95%): ₹{results['var_95']:,.2f}")
    print(f"• Value-at-Risk (VaR 99%): ₹{results['var_99']:,.2f}")
    print(f"• Tail VaR (Expected 99%): ₹{results['tvar_99_expected_shortfall']:,.2f}")
    print(f"• Suggested Commercial   : ₹{results['suggested_commercial_premium']:,.2f} (Includes 15% Risk Margin + 10% OpEx)")

    # 6. Save JSON Output Report
    output_path = "output_actuarial_report.json"
    with open(output_path, mode="w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Full actuarial report exported to: {output_path}")
    print_banner("Simulation Run Complete • Ready for Production Deployment")

if __name__ == "__main__":
    run_pipeline()
