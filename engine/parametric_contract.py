"""
Parametric Insurance Contract Module
Defines Index Payout Curves, Triggers, and Basis Risk Logic.
"""

from enum import Enum
from typing import Dict, Any

class TriggerDirection(Enum):
    DEFICIT = "DEFICIT"    # Payout triggers when index drops BELOW strike (e.g., Drought / Rainfall Deficit)
    EXCESS = "EXCESS"      # Payout triggers when index rises ABOVE strike (e.g., Heatwave / Flood / Wind Speed)

class ParametricContract:
    """
    Parametric (Index-Based) Insurance Contract.
    
    Structure:
    - Strike: Threshold where liability/payout begins.
    - Exit: Threshold where maximum payout (100% sum insured) is reached.
    - Payout escalates linearly between Strike and Exit.
    """
    def __init__(
        self,
        contract_name: str,
        index_name: str,
        strike: float,
        exit_val: float,
        max_payout: float,
        direction: TriggerDirection = TriggerDirection.DEFICIT
    ):
        self.contract_name = contract_name
        self.index_name = index_name
        self.strike = strike
        self.exit_val = exit_val
        self.max_payout = max_payout
        self.direction = direction

        # Validation
        if self.direction == TriggerDirection.DEFICIT and not (self.exit_val < self.strike):
            raise ValueError("For DEFICIT contracts, Exit must be strictly less than Strike.")
        if self.direction == TriggerDirection.EXCESS and not (self.strike < self.exit_val):
            raise ValueError("For EXCESS contracts, Strike must be strictly less than Exit.")

    def evaluate_payout(self, observed_index: float) -> Dict[str, Any]:
        """
        Calculates the financial payout for a given observed physical index value.
        """
        if self.direction == TriggerDirection.DEFICIT:
            # E.g. Rainfall: Strike = 150mm, Exit = 50mm.
            if observed_index >= self.strike:
                fraction = 0.0
            elif observed_index <= self.exit_val:
                fraction = 1.0
            else:
                fraction = (self.strike - observed_index) / (self.strike - self.exit_val)
        else:
            # E.g. Temperature: Strike = 43C, Exit = 47C.
            if observed_index <= self.strike:
                fraction = 0.0
            elif observed_index >= self.exit_val:
                fraction = 1.0
            else:
                fraction = (observed_index - self.strike) / (self.exit_val - self.strike)

        payout_amount = round(fraction * self.max_payout, 2)
        triggered = payout_amount > 0.0

        return {
            "contract": self.contract_name,
            "observed_value": round(observed_index, 2),
            "triggered": triggered,
            "payout_fraction": round(fraction, 4),
            "payout_amount": payout_amount,
            "currency": "INR"
        }
