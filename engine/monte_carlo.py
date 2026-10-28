"""
Monte Carlo Stochastic Pricing Engine
Simulates thousands of climate scenarios using Inverse Transform Sampling.
Calculates Actuarial Metrics: Expected Loss, VaR, Tail VaR, and Commercial Premium.
"""

import math
import random
from typing import List, Dict, Any
from engine.extreme_value import GumbelDistribution
from engine.parametric_contract import ParametricContract

class MonteCarloPricingEngine:
    def __init__(self, contract: ParametricContract, distribution: GumbelDistribution):
        self.contract = contract
        self.distribution = distribution

    def run_simulation(
        self,
        num_iterations: int = 10000,
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Executes N Monte Carlo iterations using Inverse Transform Sampling.
        """
        random.seed(random_seed)
        simulated_values: List[float] = []
        payouts: List[float] = []
        triggered_count = 0

        for _ in range(num_iterations):
            # Uniform random probability in (0.0001, 0.9999) to prevent math singularity
            u = random.uniform(0.0001, 0.9999)
            # Inverse CDF maps uniform random number to physical climate metric
            sim_x = self.distribution.quantile(u)
            simulated_values.append(sim_x)

            # Evaluate contract liability
            result = self.contract.evaluate_payout(sim_x)
            payout = result["payout_amount"]
            payouts.append(payout)
            if payout > 0.0:
                triggered_count += 1

        # Sort payouts for quantile / VaR computation
        sorted_payouts = sorted(payouts)

        # 1. Pure Premium (Expected Loss)
        pure_premium = sum(payouts) / num_iterations

        # 2. Claim Frequency (Trigger Probability)
        claim_frequency = triggered_count / num_iterations

        # 3. Variance & Standard Deviation
        variance = sum((p - pure_premium) ** 2 for p in payouts) / (num_iterations - 1)
        std_dev = math.sqrt(variance)

        # 4. Value-at-Risk (VaR at 95% and 99%)
        idx_95 = int(0.95 * num_iterations)
        idx_99 = int(0.99 * num_iterations)
        var_95 = sorted_payouts[min(idx_95, num_iterations - 1)]
        var_99 = sorted_payouts[min(idx_99, num_iterations - 1)]

        # 5. Tail Value-at-Risk (TVaR / Expected Shortfall at 99%)
        tail_99_losses = sorted_payouts[idx_99:]
        tvar_99 = (sum(tail_99_losses) / len(tail_99_losses)) if tail_99_losses else var_99

        # 6. Commercial Premium Breakdown
        # Actuarial Rule: Pure Premium + Capital Reserve Margin (e.g. 15% of StdDev) + Expense Ratio (e.g. 10%)
        risk_margin = 0.15 * std_dev
        expense_loading = 0.10 * pure_premium
        commercial_premium = pure_premium + risk_margin + expense_loading
        burn_rate_pct = (pure_premium / self.contract.max_payout) * 100.0

        return {
            "iterations": num_iterations,
            "contract_name": self.contract.contract_name,
            "sum_insured": self.contract.max_payout,
            "pure_premium": round(pure_premium, 2),
            "burn_rate_pct": round(burn_rate_pct, 2),
            "claim_frequency_pct": round(claim_frequency * 100.0, 2),
            "standard_deviation": round(std_dev, 2),
            "var_95": round(var_95, 2),
            "var_99": round(var_99, 2),
            "tvar_99_expected_shortfall": round(tvar_99, 2),
            "suggested_commercial_premium": round(commercial_premium, 2),
            "currency": "INR"
        }
