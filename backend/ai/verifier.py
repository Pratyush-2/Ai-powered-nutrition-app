"""
Verification module for macro claims and nutritional calculations.

This module verifies LLM-generated nutritional claims against retrieved facts
and provides auto-correction when discrepancies are found.
"""

import logging
from typing import Dict, List, Tuple, Optional
import re

logger = logging.getLogger(__name__)

class NutritionVerifier:
    """Verifies nutritional claims and provides corrections."""
    
    def __init__(self, tolerance_percent: float = 5.0):
        self.tolerance_percent = tolerance_percent
    
    def extract_nutritional_values(self, text: str) -> Dict[str, float]:
        """
        Extract nutritional values from text using regex patterns.
        
        Args:
            text: Text containing nutritional information
            
        Returns:
            Dictionary with extracted values
        """
        values = {}
        
        # Patterns for different nutritional values
        patterns = {
            'calories': [
                r'(\d+(?:\.\d+)?)\s*(?:kcal|calories?|cal)',
                r'(\d+(?:\.\d+)?)\s*cal'
            ],
            'protein': [
                r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*protein',
                r'(\d+(?:\.\d+)?)\s*protein'
            ],
            'carbs': [
                r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*(?:carbs|carbohydrates?)',
                r'(\d+(?:\.\d+)?)\s*(?:carbs|carbohydrates?)'
            ],
            'fat': [
                r'(\d+(?:\.\d+)?)\s*(?:g|grams?)\s*fat',
                r'(\d+(?:\.\d+)?)\s*fat'
            ]
        }
        
        for nutrient, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        values[nutrient] = float(matches[0])
                        break
                    except ValueError:
                        continue
        
        return values
    
    def calculate_expected_values(self, retrieved_facts: List[Dict], 
                                suggested_portions: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate expected nutritional values based on retrieved facts and portions.
        
        Args:
            retrieved_facts: List of retrieved nutrition facts
            suggested_portions: Dictionary with food names and suggested portions (in grams)
            
        Returns:
            Dictionary with calculated nutritional values
        """
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for fact in retrieved_facts:
            food_name = fact.get('meta', {}).get('name', '')
            portion = suggested_portions.get(food_name, 100)  # Default to 100g
            
            # Scale nutrition values to portion size
            calories_per_100g = fact.get('meta', {}).get('calories_100g', 0)
            protein_per_100g = fact.get('meta', {}).get('protein_100g', 0)
            carbs_per_100g = fact.get('meta', {}).get('carbs_100g', 0)
            fat_per_100g = fact.get('meta', {}).get('fat_100g', 0)
            
            # Calculate values for the portion
            scale_factor = portion / 100
            total_calories += calories_per_100g * scale_factor
            total_protein += protein_per_100g * scale_factor
            total_carbs += carbs_per_100g * scale_factor
            total_fat += fat_per_100g * scale_factor
        
        return {
            'calories': total_calories,
            'protein': total_protein,
            'carbs': total_carbs,
            'fat': total_fat
        }
    
    def verify_macro_claims(self, plan: str, retrieved_facts: List[Dict], 
                          suggested_portions: Dict[str, float] = None) -> Dict:
        """
        Verify macro claims in a meal plan against retrieved facts.
        
        Args:
            plan: LLM-generated meal plan text
            retrieved_facts: Retrieved nutrition facts
            suggested_portions: Suggested portions for each food
            
        Returns:
            Verification result with status and corrections
        """
        if not retrieved_facts:
            return {
                'status': 'no_evidence',
                'message': 'No retrieved facts available for verification',
                'corrected_plan': plan
            }
        
        # Extract claimed values from the plan
        claimed_values = self.extract_nutritional_values(plan)
        
        if not claimed_values:
            return {
                'status': 'no_claims',
                'message': 'No nutritional claims found in the plan',
                'corrected_plan': plan
            }
        
        # Calculate expected values
        if suggested_portions is None:
            suggested_portions = {fact.get('meta', {}).get('name', ''): 100 for fact in retrieved_facts}
        
        expected_values = self.calculate_expected_values(retrieved_facts, suggested_portions)
        
        # Compare claimed vs expected values
        discrepancies = []
        tolerance = self.tolerance_percent / 100
        
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            if nutrient in claimed_values and nutrient in expected_values:
                claimed = claimed_values[nutrient]
                expected = expected_values[nutrient]
                
                if expected > 0:
                    difference = abs(claimed - expected) / expected
                    if difference > tolerance:
                        discrepancies.append({
                            'nutrient': nutrient,
                            'claimed': claimed,
                            'expected': expected,
                            'difference_percent': difference * 100
                        })
        
        # Generate verification result
        if not discrepancies:
            return {
                'status': 'verified',
                'message': 'All nutritional claims are within acceptable tolerance',
                'claimed_values': claimed_values,
                'expected_values': expected_values,
                'corrected_plan': plan
            }
        else:
            # Generate corrected plan
            corrected_plan = self._generate_corrected_plan(plan, claimed_values, expected_values)
            
            return {
                'status': 'discrepancies_found',
                'message': f'Found {len(discrepancies)} discrepancies exceeding {self.tolerance_percent}% tolerance',
                'discrepancies': discrepancies,
                'claimed_values': claimed_values,
                'expected_values': expected_values,
                'corrected_plan': corrected_plan
            }
    
    def _generate_corrected_plan(self, original_plan: str, claimed_values: Dict, 
                               expected_values: Dict) -> str:
        """Generate a corrected version of the meal plan."""
        corrected_plan = original_plan
        
        # Replace claimed values with expected values
        for nutrient in ['calories', 'protein', 'carbs', 'fat']:
            if nutrient in claimed_values and nutrient in expected_values:
                claimed = claimed_values[nutrient]
                expected = expected_values[nutrient]
                
                # Find and replace the claimed value
                pattern = rf'{claimed:.1f}(?=\s*(?:kcal|calories?|cal|g|grams?))'
                replacement = f'{expected:.1f}'
                corrected_plan = re.sub(pattern, replacement, corrected_plan, flags=re.IGNORECASE)
        
        # Add correction note
        correction_note = f"\n\n[Corrected: Values updated based on verified nutritional data]"
        corrected_plan += correction_note
        
        return corrected_plan
    
    def validate_portion_sizes(self, suggested_portions: Dict[str, float]) -> Dict:
        """
        Validate that suggested portion sizes are reasonable.
        
        Args:
            suggested_portions: Dictionary with food names and portions
            
        Returns:
            Validation result
        """
        warnings = []
        
        for food, portion in suggested_portions.items():
            # Check for extremely large portions
            if portion > 500:  # More than 500g
                warnings.append(f"Large portion size for {food}: {portion}g")
            
            # Check for extremely small portions
            if portion < 10:  # Less than 10g
                warnings.append(f"Very small portion size for {food}: {portion}g")
        
        return {
            'status': 'valid' if not warnings else 'warnings',
            'warnings': warnings,
            'suggested_portions': suggested_portions
        }
    
    def get_verification_summary(self, verification_result: Dict) -> str:
        """Generate a human-readable verification summary."""
        status = verification_result['status']
        
        if status == 'verified':
            return "✅ All nutritional claims verified against available data."
        
        elif status == 'discrepancies_found':
            discrepancies = verification_result['discrepancies']
            summary = f"⚠️ Found {len(discrepancies)} discrepancies:\n"
            
            for disc in discrepancies:
                summary += f"  • {disc['nutrient']}: claimed {disc['claimed']:.1f}, expected {disc['expected']:.1f} "
                summary += f"(difference: {disc['difference_percent']:.1f}%)\n"
            
            return summary.strip()
        
        elif status == 'no_evidence':
            return "❌ No nutritional data available for verification."
        
        elif status == 'no_claims':
            return "ℹ️ No specific nutritional claims found to verify."
        
        else:
            return f"❓ Verification status: {status}"


# Global verifier instance
_verifier_instance = None

def get_verifier() -> NutritionVerifier:
    """Get the global verifier instance."""
    global _verifier_instance
    if _verifier_instance is None:
        _verifier_instance = NutritionVerifier()
    return _verifier_instance

def verify_macro_claims(plan: str, retrieved_facts: List[Dict], 
                       suggested_portions: Dict[str, float] = None) -> Dict:
    """Convenience function to verify macro claims."""
    verifier = get_verifier()
    return verifier.verify_macro_claims(plan, retrieved_facts, suggested_portions)

