"""
Extreme Value Theory (EVT) Module
Implements Gumbel (Type I Extreme Value) Distribution for Climate Risk Analysis.
Zero external dependency implementation using pure Python mathematics.
"""

import math
from typing import List, Tuple, Dict

class GumbelDistribution:
    """
    Gumbel Maximum Distribution.
    CDF: F(x) = exp(-exp(-(x - mu) / beta))
    Quantile (Inverse CDF): Q(p) = mu - beta * ln(-ln(p))
    """
    def __init__(self, mu: float, beta: float):
        if beta <= 0:
            raise ValueError("Scale parameter beta must be strictly positive.")
        self.mu = mu        # Location parameter
        self.beta = beta    # Scale parameter

    def cdf(self, x: float) -> float:
        """Computes Cumulative Distribution Function P(X <= x)."""
        z = (x - self.mu) / self.beta
        return math.exp(-math.exp(-z))

    def exceedance_probability(self, x: float) -> float:
        """Computes survival function P(X > x) = 1 - F(x)."""
        return 1.0 - self.cdf(x)

    def quantile(self, p: float) -> float:
        """
        Inverse CDF (Quantile Function).
        Given probability p in (0, 1), returns value x such that F(x) = p.
        Used for Monte Carlo inverse transform sampling.
        """
        if not (0.0 < p < 1.0):
            raise ValueError("Probability p must be in open interval (0, 1).")
        return self.mu - self.beta * math.log(-math.log(p))

    def return_level(self, return_period_years: float) -> float:
        """
        Calculates the physical value corresponding to a T-year return period.
        T = 1 / (1 - F(x))  =>  F(x) = 1 - 1/T
        """
        if return_period_years <= 1.0:
            raise ValueError("Return period must be > 1.0 year.")
        p = 1.0 - (1.0 / return_period_years)
        return self.quantile(p)

    @classmethod
    def fit_moments(cls, sample: List[float]) -> "GumbelDistribution":
        """
        Fits Gumbel parameters using Method of Moments.
        Mean = mu + gamma * beta  (where gamma is Euler-Mascheroni constant ~ 0.57721566)
        Variance = (pi^2 / 6) * beta^2
        """
        n = len(sample)
        if n < 5:
            raise ValueError("Sample size must be at least 5 for EVT fitting.")

        mean_val = sum(sample) / n
        var_val = sum((x - mean_val) ** 2 for x in sample) / (n - 1)
        std_val = math.sqrt(var_val)

        euler_mascheroni = 0.57721566490153286
        beta = (std_val * math.sqrt(6)) / math.pi
        mu = mean_val - (euler_mascheroni * beta)

        return cls(mu=mu, beta=beta)

    def generate_return_period_table(self, periods: List[float] = None) -> List[Dict[str, float]]:
        """Generates actuarial return period summary table."""
        if periods is None:
            periods = [2.0, 5.0, 10.0, 20.0, 50.0, 100.0]

        table = []
        for t in periods:
            val = self.return_level(t)
            p_exceed = 1.0 / t
            table.append({
                "return_period_years": t,
                "annual_exceedance_prob": round(p_exceed, 4),
                "threshold_value": round(val, 2)
            })
        return table
