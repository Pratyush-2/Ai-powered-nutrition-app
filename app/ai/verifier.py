"""Verifier for nutrition claims."""

import re
from typing import Dict, List


class NutritionVerifier:
    """Verifies nutrition claims against facts."""

    def __init__(self, tolerance_percent=5.0):
        """Initialize the verifier."""
        self.tolerance_percent = tolerance_percent

    def _extract_claimed_values(self, plan: str) -> Dict[str, float]:
        """Extract claimed nutrition values from text."""
        patterns = {
            "calories": r"(\d+)\s*(?:kcal|calories)",
            "protein": r"(\d+)g\s*protein",
            "carbs": r"(\d+)g\s*carbs",
            "fat": r"(\d+)g\s*fat"
        }
        
        values = {}
        for nutrient, pattern in patterns.items():
            match = re.search(pattern, plan.lower())
            if match:
                values[nutrient] = float(match.group(1))
        return values

    def _calculate_expected_values(self, facts: List[Dict], portions: Dict[str, float]) -> Dict[str, float]:
        """Calculate expected nutrition values."""
        expected = {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0
        }
        
        for fact in facts:
            meta = fact["meta"]
            food_name = meta["name"]
            if food_name in portions:
                portion_g = portions[food_name]
                multiplier = portion_g / 100.0  # Convert to per-portion values
                
                expected["calories"] += meta["calories_100g"] * multiplier
                expected["protein"] += meta["protein_100g"] * multiplier
                expected["carbs"] += meta["carbs_100g"] * multiplier
                expected["fat"] += meta["fat_100g"] * multiplier
        
        return {k: round(v, 1) for k, v in expected.items()}

    def _values_match(self, claimed: float, expected: float) -> bool:
        """Check if values match within tolerance."""
        if claimed == 0 and expected == 0:
            return True
        
        if claimed == 0 or expected == 0:
            return False
        
        percent_diff = abs(claimed - expected) / expected * 100
        return percent_diff <= self.tolerance_percent

    def verify_macro_claims(self, plan: str, retrieved_facts: List[Dict], suggested_portions: Dict[str, float]) -> Dict:
        """Verify nutrition claims against retrieved facts."""
        claimed_values = self._extract_claimed_values(plan)
        expected_values = self._calculate_expected_values(retrieved_facts, suggested_portions)
        
        mismatches = []
        for nutrient in ["calories", "protein", "carbs", "fat"]:
            if nutrient in claimed_values and nutrient in expected_values:
                if not self._values_match(claimed_values[nutrient], expected_values[nutrient]):
                    mismatches.append(nutrient)
        
        corrected_plan = plan
        if mismatches:
            for nutrient in mismatches:
                old_value = f"{claimed_values[nutrient]}"
                new_value = f"{expected_values[nutrient]}"
                corrected_plan = re.sub(
                    f"({old_value}\\s*(?:kcal|g)\\s*{nutrient})",
                    f"{new_value}g {nutrient}",
                    corrected_plan,
                    flags=re.IGNORECASE
                )
        
        return {
            "status": "verified" if not mismatches else "corrected",
            "claimed_values": claimed_values,
            "expected_values": expected_values,
            "corrected_plan": corrected_plan,
            "mismatches": mismatches
        }