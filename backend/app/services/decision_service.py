"""
Cloud Agronomic Decision Service
Implements FAO-56 logic to validate incoming telemetry and generate actionable advisory.
"""

from typing import Dict, Any


class DecisionService:
    CROP_PROFILES = {
        "maize": {
            "display_name": "Maize",
            "threshold_ec": 1.7,
            "slope_percent": 12.0,
            "min_moisture_vwc": 22.0,
            "max_moisture_vwc": 38.0,
            "standard_npk_dose": "3.5 kg / 100m²"
        },
        "tomato": {
            "display_name": "Tomato",
            "threshold_ec": 2.5,
            "slope_percent": 9.9,
            "min_moisture_vwc": 25.0,
            "max_moisture_vwc": 40.0,
            "standard_npk_dose": "2.8 kg / 100m²"
        },
        "rice": {
            "display_name": "Rice",
            "threshold_ec": 3.0,
            "slope_percent": 12.0,
            "min_moisture_vwc": 35.0,
            "max_moisture_vwc": 55.0,
            "standard_npk_dose": "4.0 kg / 100m²"
        },
        "wheat": {
            "display_name": "Wheat",
            "threshold_ec": 6.0,
            "slope_percent": 7.1,
            "min_moisture_vwc": 20.0,
            "max_moisture_vwc": 35.0,
            "standard_npk_dose": "3.0 kg / 100m²"
        }
    }

    @classmethod
    def get_crop(cls, crop_name: str) -> Dict[str, Any]:
        return cls.CROP_PROFILES.get(str(crop_name).lower(), cls.CROP_PROFILES["maize"])

    @classmethod
    def normalize_temperature(cls, raw_ec: float, temp_c: float) -> float:
        """Standardizes EC to 25°C baseline using Rhoades USDA coefficient (1.91%/°C)"""
        alpha = 0.0191
        factor = 1.0 + alpha * (temp_c - 25.0)
        if factor <= 0.1:
            factor = 0.1
        return round(max(0.0, raw_ec / factor), 2)

    @classmethod
    def calculate_leaching_requirement(cls, ec_soil_target: float, ec_water: float = 0.6) -> float:
        """
        FAO-56 / FAO-29 Leaching Fraction calculation.
        Enforces safety guard: when ECw > 0.5 * ECe, leaching is locked out to prevent salt buildup.
        """
        if ec_water > 0.5 * ec_soil_target:
            return 0.0

        denom = (5.0 * ec_soil_target) - ec_water
        if denom <= 0:
            return 0.15
        lr = ec_water / denom
        return round(min(max(lr, 0.05), 0.45), 2)

    @classmethod
    def evaluate(cls, crop_name: str, raw_ec: float, temp_c: float, moisture_vwc: float, ec_water: float = 0.6) -> Dict[str, Any]:
        crop = cls.get_crop(crop_name)
        ec_25 = cls.normalize_temperature(raw_ec, temp_c)
        threshold_ec = crop["threshold_ec"]
        slope = crop["slope_percent"]
        min_moist = crop["min_moisture_vwc"]
        max_moist = crop["max_moisture_vwc"]

        is_saline = ec_25 > threshold_ec
        is_dry = moisture_vwc < min_moist
        is_waterlogged = moisture_vwc > max_moist

        yield_loss = 0.0
        if is_saline:
            yield_loss = round(min((ec_25 - threshold_ec) * slope, 100.0), 1)

        # 1. Critical Salinity
        if is_saline:
            lr = cls.calculate_leaching_requirement(threshold_ec, ec_water)
            extra_percent = int(lr * 100)
            return {
                "crop_name": crop["display_name"],
                "status": "CRITICAL",
                "action": "FLUSH_SALTS",
                "allow_fertilizer": False,
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": lr,
                "extra_water_percent": extra_percent,
                "projected_yield_loss_percent": yield_loss,
                "fertilizer_guidance": "LOCKED: Hold all fertilizer. Soil salt concentration is toxic.",
                "advisory_message": f"Hold fertilizer! Soil salt high ({ec_25} dS/m). Water with {extra_percent}% extra volume to leach salts."
            }

        # 2. Dry soil
        if is_dry:
            return {
                "crop_name": crop["display_name"],
                "status": "IRRIGATE",
                "action": "WATER_FIELD",
                "allow_fertilizer": True,
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": 0.0,
                "extra_water_percent": 0,
                "projected_yield_loss_percent": 0.0,
                "fertilizer_guidance": f"OK: Standard dosage recommended: {crop['standard_npk_dose']}.",
                "advisory_message": f"Soil dry ({moisture_vwc}%). Salinity safe ({ec_25} dS/m). Run standard irrigation."
            }

        # 3. Waterlogged
        if is_waterlogged:
            return {
                "crop_name": crop["display_name"],
                "status": "CAUTION",
                "action": "PAUSE_WATER",
                "allow_fertilizer": False,
                "normalized_ec_25": ec_25,
                "threshold_ec": threshold_ec,
                "leaching_fraction": 0.0,
                "extra_water_percent": 0,
                "projected_yield_loss_percent": 0.0,
                "fertilizer_guidance": "LOCKED: Soil saturated. Risk of fertilizer leaching runoff.",
                "advisory_message": f"Soil saturated ({moisture_vwc}%). Pause irrigation to prevent root hypoxia."
            }

        # 4. Optimal
        return {
            "crop_name": crop["display_name"],
            "status": "OPTIMAL",
            "action": "NONE",
            "allow_fertilizer": True,
            "normalized_ec_25": ec_25,
            "threshold_ec": threshold_ec,
            "leaching_fraction": 0.0,
            "extra_water_percent": 0,
            "projected_yield_loss_percent": 0.0,
            "fertilizer_guidance": f"OPTIMAL: Safe application window: {crop['standard_npk_dose']}.",
            "advisory_message": f"All metrics balanced (EC: {ec_25} dS/m, Moisture: {moisture_vwc}%). Soil conditions healthy."
        }
