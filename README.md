# 🌪️ ParamRisk — Parametric Climate Risk & Actuarial Pricing Engine

[![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Build Status](https://img.shields.io/badge/Tests-8%20Passed-emerald)](tests/)
[![Domain](https://img.shields.io/badge/Domain-Climate%20Insurtech%20%26%20Parametric%20Risk-purple)](https://github.com/nilesh7757/paramRisk)
[![License](https://img.shields.io/badge/License-MIT-slate)](LICENSE)

An open-source quantitative modeling engine for **Parametric (Index-Based) Climate Insurance**, developed for high-precision disaster risk financing, drought protection, and heatwave resilience across agricultural and urban regions in India.

Built from first principles in pure Python (zero external library dependency required for core execution).

---

## 🏛️ Executive Summary: Why Parametric Insurance?

Traditional indemnity insurance suffers from long settlement delays, high loss-adjustment expenses, and claims friction (e.g., waiting months for an insurance surveyor to inspect field damage).

**Parametric Insurance** replaces manual damage assessment with **predefined, objective physical triggers**:
* When a verified climate index breaches a threshold (e.g., 30-day cumulative rainfall $< 60\text{ mm}$ or maximum temperature $> 44^\circ\text{C}$), **payouts are triggered automatically and settled within 48 to 72 hours**.
* Zero loss adjustment costs. Zero claims disputes. Immediate liquidity for affected farmers and vulnerable daily-wage workers.

---

## 🔬 Mathematical & Actuarial Architecture

```
[ Historical Climate Records (1995-2025) ]
                    │
                    ▼
[ Extreme Value Theory (EVT) Gumbel Fitting ]
                    │
                    ▼
[ Actuarial Return Period Analysis (1-in-10, 1-in-50 yr) ]
                    │
                    ▼
[ Parametric Contract Calibration (Strike & Exit Thresholds) ]
                    │
                    ▼
[ Monte Carlo Stochastic Simulation (10,000 Iterations) ]
                    │
                    ▼
[ Solvency Metrics: Pure Premium, VaR (99%), Tail VaR, Commercial Pricing ]
```

### 1. Extreme Value Theory (EVT) & Gumbel Distribution
Standard normal (Gaussian) distributions drastically underestimate tail climate risk. We model annual maximum heatwaves and drought precipitation deficits using the **Gumbel Maximum Distribution (Type I Generalized Extreme Value)**:

$$\text{CDF: } F(x; \mu, \beta) = \exp\left(-\exp\left(-\frac{x - \mu}{\beta}\right)\right)$$

$$\text{Quantile (Inverse CDF): } Q(p; \mu, \beta) = \mu - \beta \ln(-\ln(p)) \quad \text{for } p \in (0, 1)$$

### 2. Actuarial Return Period ($T$) Formulation
The physical threshold corresponding to a $T$-year return period event is computed as:

$$x_T = \mu - \beta \ln\left(-\ln\left(1 - \frac{1}{T}\right)\right)$$

### 3. Parametric Linear Payout Function
Between the **Strike Threshold** ($T_{\text{strike}}$: where payout starts) and **Exit Threshold** ($T_{\text{exit}}$: where 100% max sum insured is paid):

$$\text{Payout}(x) = \begin{cases} 
0 & \text{if } x \le T_{\text{strike}} \\
\text{Max Payout} \times \frac{x - T_{\text{strike}}}{T_{\text{exit}} - T_{\text{strike}}} & \text{if } T_{\text{strike}} < x < T_{\text{exit}} \\
\text{Max Payout} & \text{if } x \ge T_{\text{exit}}
\end{cases}$$

### 4. Monte Carlo Stochastic Pricing & Solvency
Using **Inverse Transform Sampling**, the engine runs 10,000 synthetic seasons to determine:
* **Pure Premium (Expected Loss)**: $\mathbb{E}[\text{Payout}] = \frac{1}{N} \sum_{i=1}^N \text{Payout}_i$
* **Burn Rate**: $\frac{\mathbb{E}[\text{Payout}]}{\text{Max Sum Insured}}$
* **Value-at-Risk at 99% ($\text{VaR}_{0.99}$)**: The 99th percentile loss.
* **Tail Value-at-Risk ($\text{TVaR}_{0.99}$ / Expected Shortfall)**: Average loss in the worst 1% of catastrophe seasons.
* **Commercial Premium**: $\text{Pure Premium} + \text{Risk Margin (15\% of }\sigma\text{)} + \text{Expense Loading (10\%)}$.

---

## ⚡ Quickstart & Execution

### 1. Clone the Repository
```bash
git clone https://github.com/nilesh7757/paramRisk.git
cd paramRisk
```

### 2. Run the Unit Test Suite (8/8 Tests)
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### 3. Execute the End-to-End Simulation Pipeline
```bash
python3 main.py
```

---

## 📊 Sample Output (10,000 Stochastic Iterations)

```text
==============================================================================
  STEP 1: EXTREME VALUE THEORY (EVT) PARAMETER ESTIMATION
==============================================================================
• Saurashtra Rainfall Deficit Gumbel Parameters:
  Location (mu): 104.13 mm | Scale (beta): 81.34 mm
• Ahmedabad Max Summer Temperature Gumbel Parameters:
  Location (mu): 40.46 °C | Scale (beta): 1.73 °C

==============================================================================
  STEP 2: ACTUARIAL CLIMATE RETURN PERIOD TABLE (AHMEDABAD HEATWAVE)
==============================================================================
Return Period (Years)    | Exceedance Prob    | Design Max Temp (°C)  
------------------------------------------------------------------------
2                        | 0.5000             | 41.09                 
5                        | 0.2000             | 43.04                 
10                       | 0.1000             | 44.34                 
25                       | 0.0400             | 45.97                 
50                       | 0.0200             | 47.19                 
100                      | 0.0100             | 48.39                 

==============================================================================
  STEP 4: MONTE CARLO ACTUARIAL PRICING (10,000 STOCHASTIC ITERATIONS)
==============================================================================
Contract Evaluated: Ahmedabad Urban Daily-Wage Heatwave Shield
• Total Iterations       : 10,000
• Trigger Claim Frequency: 11.51% of seasons
• Pure Premium (Expected): ₹797.91 (5.32% Burn Rate)
• Standard Deviation     : ₹2,785.35
• Value-at-Risk (VaR 95%): ₹6,948.44
• Value-at-Risk (VaR 99%): ₹15,000.00
• Tail VaR (Expected 99%): ₹15,000.00
• Suggested Commercial   : ₹1,295.50 (Includes 15% Risk Margin + 10% OpEx)
```

---

## 📁 Repository Structure

```
analysis_project/
├── engine/
│   ├── __init__.py
│   ├── extreme_value.py        # Gumbel fitting, EVT return period calculations
│   ├── parametric_contract.py  # Linear payout curve, strike & exit thresholds
│   └── monte_carlo.py          # 10,000-run stochastic simulation & VaR / TVaR
├── data/
│   ├── historical_climate_data.csv  # 30-year climate records (Gujarat districts)
│   └── generate_sample_data.py      # Reproducible dataset generator
├── tests/
│   └── test_engine.py          # Unit test verification suite (100% pass)
├── main.py                     # CLI pipeline driver
├── output_actuarial_report.json # Actuarial simulation output
├── requirements.txt
└── README.md
```

---

## 👨‍💻 Author & Academic Attribution
* **Author**: Nilesh Mori
* **Institution**: Dhirubhai Ambani Institute of Information and Communication Technology (DA-IICT)
* **Degree**: B.Tech (Hons.) in ICT with Minor in Computational Science (Batch 2023–2027)
* **Profiles**: [GitHub](https://github.com/nilesh7757) • [LeetCode (1831 Knight)](https://leetcode.com/nileshmori7757/) • [LinkedIn](https://www.linkedin.com/in/nileshmori7757/)

---

## 📜 License
Licensed under the [MIT License](LICENSE).
