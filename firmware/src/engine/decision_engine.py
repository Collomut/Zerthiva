"""
SoilGuard Agronomic Decision Engine (FAO-56 Implementation)
Evaluates real-time soil vectors and determines irrigation, leaching, and fertilizer directives.
"""

from .fao_tables import get_crop_profile


class DecisionEngine:
    def __init__(self, ec_water_source: float = 0.6):
        """
        :param ec_water_source: Electrical conductivity of irrigation water source in dS/m
        """
        self.ec_water = float(ec_water_source)

    def normalize_temperature(self, raw_ec: float, temp_c: float) -> float:
        """
        Standardizes electrical conductivity to 25°C baseline.
        EC_25 = EC_raw / (1 + 0.02 * (T - 25))
        """
        alpha = 0.020
        temp_factor = 1.0 + alpha * (temp_c - 25.0)
        if temp_factor <= 0.1:
            temp_factor = 0.1
        normalized = raw_ec / temp_factor
        return round(max(0.0, normalized), 2)

    def calculate_leaching_requirement(self, ec_soil_target: float) -> float:
        """
        FAO-56 standard Leaching Requirement (LR) formula:
        LR = ECw / (5 * ECe - ECw)
        """
        denominator = (5.0 * ec_soil_target) - self.ec_water
        if denominator <= 0:
            return 0.15 # Fallback baseline 15% leaching buffer
        lr = self.ec_water / denominator
        # Clamp leaching fraction between 5% and 45%
        return round(min(max(lr, 0.05), 0.45), 2)

    def calculate_yield_loss(self, ec_25: float, threshold_ec: float, slope_percent: float) -> float:
        """Computes estimated yield decline percentage if salt stress is sustained"""
        if ec_25 <= threshold_ec:
            return 0.0
        excess_ec = ec_25 - threshold_ec
        loss = excess_ec * slope_percent
        return round(min(loss, 100.0), 1)

    def evaluate(self, crop_name: str, raw_ec: float, temp_c: float, moisture_vwc: float) -> dict:
        """
        Analyzes field vectors and produces an actionable agronomic prescription.
        """
        crop = get_crop_profile(crop_name)
        ec_25 = self.normalize_temperature(raw_ec, temp_c)
        threshold_ec = crop["threshold_ec"]
        slope = crop["slope_percent"]
        min_moist = crop["min_moisture_vwc"]
        max_moist = crop["max_moisture_vwc"]

        is_saline = ec_25 > threshold_ec
        is_dry = moisture_vwc < min_moist
        is_waterlogged = moisture_vwc > max_moist
        yield_loss = self.calculate_yield_loss(ec_25, threshold_ec, slope)

        # 1. CRITICAL: High Soil Salinity (Root Zone Salt Accumulation)
        if is_saline:
            lr = self.calculate_leaching_requirement(threshold_ec)
            extra_percent = int(lr * 100)
            return {
                "status": "CRITICAL",
                "led_color": "RED",
                "allow_fertilizer": False,
                "action": "FLUSH_SALTS",
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": lr,
                "extra_water_percent": extra_percent,
                "projected_yield_loss_percent": yield_loss,
                "fertilizer_guidance": "LOCKED: Hold all fertilizers. Soil salinity is high.",
                "sms_message": f"SoilGuard Alert: High salt in {crop['display_name']} ({ec_25} dS/m > {threshold_ec}). Hold fertilizer! Flush with {extra_percent}% extra irrigation water.",
                "summary": f"Salinity exceeds threshold ({ec_25} vs {threshold_ec} dS/m). Leaching cycle required."
            }

        # 2. IRRIGATE: Dry Soil (Salinity within safe range)
        if is_dry:
            return {
                "status": "IRRIGATE",
                "led_color": "YELLOW",
                "allow_fertilizer": True,
                "action": "WATER_FIELD",
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": 0.0,
                "extra_water_percent": 0,
                "projected_yield_loss_percent": 0.0,
                "fertilizer_guidance": f"OK: Standard dosage recommended: {crop['standard_npk_dose']}.",
                "sms_message": f"SoilGuard: Soil moisture is low ({moisture_vwc}%). Salinity is safe ({ec_25} dS/m). Run normal irrigation today.",
                "summary": f"Moisture is below refill point ({moisture_vwc}% < {min_moist}%). Standard irrigation recommended."
            }

        # 3. CAUTION: Waterlogged Soil (Risk of Hypoxia and Root Rot)
        if is_waterlogged:
            return {
                "status": "CAUTION",
                "led_color": "YELLOW",
                "allow_fertilizer": False,
                "action": "PAUSE_WATER",
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": 0.0,
                "extra_water_percent": 0,
                "projected_yield_loss_percent": 0.0,
                "fertilizer_guidance": "LOCKED: Soil saturated. Fertilizer application will cause chemical runoff.",
                "sms_message": f"SoilGuard Caution: Soil saturated ({moisture_vwc}%). Pause irrigation to prevent root rot.",
                "summary": f"Soil moisture exceeds field capacity ({moisture_vwc}% > {max_moist}%). Pause watering."
            }

        # 4. OPTIMAL: Balanced Field Equilibrium
        return {
            "status": "OPTIMAL",
            "led_color": "GREEN",
            "allow_fertilizer": True,
            "action": "NONE",
            "normalized_ec_25": ec_25,
            "threshold_ec": threshold_ec,
            "leaching_fraction": 0.0,
            "extra_water_percent": 0,
            "projected_yield_loss_percent": 0.0,
            "fertilizer_guidance": f"OPTIMAL: Safe window for scheduled application: {crop['standard_npk_dose']}.",
            "sms_message": f"SoilGuard: All soil metrics optimal (EC: {ec_25} dS/m, Moisture: {moisture_vwc}%). No action needed.",
            "summary": "Soil salinity and moisture levels are within optimal agronomic targets."
        }
