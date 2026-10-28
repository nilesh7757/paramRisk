"""
Unit Test Suite for Parametric Climate Risk Engine
Verifies mathematical properties of EVT, contract triggers, and Monte Carlo pricing.
"""

import unittest
from engine.extreme_value import GumbelDistribution
from engine.parametric_contract import ParametricContract, TriggerDirection
from engine.monte_carlo import MonteCarloPricingEngine

class TestExtremeValueTheory(unittest.TestCase):
    def setUp(self):
        # Sample annual maximum temperatures in Gujarat
        self.sample_temps = [42.1, 44.5, 41.8, 46.2, 43.0, 45.1, 47.3, 42.8, 43.9, 45.8]
        self.dist = GumbelDistribution.fit_moments(self.sample_temps)

    def test_parameters_positive(self):
        self.assertGreater(self.dist.beta, 0.0)
        self.assertGreater(self.dist.mu, 30.0)

    def test_cdf_bounds(self):
        self.assertAlmostEqual(self.dist.cdf(-100.0), 0.0, places=4)
        self.assertAlmostEqual(self.dist.cdf(100.0), 1.0, places=4)

    def test_quantile_inversion(self):
        # Q(F(x)) should approximately equal x
        test_x = 44.0
        p = self.dist.cdf(test_x)
        reconstructed_x = self.dist.quantile(p)
        self.assertAlmostEqual(test_x, reconstructed_x, places=5)

    def test_return_period_monotonicity(self):
        # 50-year return level must strictly exceed 10-year return level
        r10 = self.dist.return_level(10.0)
        r50 = self.dist.return_level(50.0)
        self.assertGreater(r50, r10)

class TestParametricContract(unittest.TestCase):
    def setUp(self):
        # Drought contract: Strike = 150mm, Exit = 50mm, Max Payout = ₹40,000/ha
        self.contract = ParametricContract(
            contract_name="Saurashtra Groundnut Drought Shield",
            index_name="Cumulative Monsoon Sowing Rainfall (mm)",
            strike=150.0,
            exit_val=50.0,
            max_payout=40000.0,
            direction=TriggerDirection.DEFICIT
        )

    def test_zero_payout_above_strike(self):
        res = self.contract.evaluate_payout(180.0)
        self.assertEqual(res["payout_amount"], 0.0)
        self.assertFalse(res["triggered"])

    def test_full_payout_below_exit(self):
        res = self.contract.evaluate_payout(40.0)
        self.assertEqual(res["payout_amount"], 40000.0)
        self.assertEqual(res["payout_fraction"], 1.0)
        self.assertTrue(res["triggered"])

    def test_linear_interpolation(self):
        # At midpoint 100mm, payout fraction must be exactly 0.5 (₹20,000)
        res = self.contract.evaluate_payout(100.0)
        self.assertEqual(res["payout_amount"], 20000.0)
        self.assertEqual(res["payout_fraction"], 0.5)

class TestMonteCarloEngine(unittest.TestCase):
    def test_simulation_metrics(self):
        dist = GumbelDistribution(mu=42.5, beta=1.8)
        contract = ParametricContract(
            contract_name="Extreme Heat Shield",
            index_name="Max Temperature (C)",
            strike=43.5,
            exit_val=47.5,
            max_payout=25000.0,
            direction=TriggerDirection.EXCESS
        )
        engine = MonteCarloPricingEngine(contract, dist)
        results = engine.run_simulation(num_iterations=2000, random_seed=42)

        self.assertGreater(results["pure_premium"], 0.0)
        self.assertLess(results["pure_premium"], 25000.0)
        self.assertGreaterEqual(results["var_99"], results["var_95"])
        self.assertGreaterEqual(results["tvar_99_expected_shortfall"], results["var_99"])

if __name__ == "__main__":
    unittest.main()
