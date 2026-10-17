"""
Sensor Anomaly & Outlier Detector
Filters out physical hardware faults, floating ADC pins, and impossible environmental readings.
"""

from typing import Tuple, List


class AnomalyDetector:
    # Physical plausibility limits for tropical/temperate agricultural soils
    LIMITS = {
        "raw_ec": {"min": 0.0, "max": 20.0},
        "soil_temp_c": {"min": -10.0, "max": 65.0},
        "moisture_vwc": {"min": 0.0, "max": 100.0},
        "battery_voltage": {"min": 2.5, "max": 4.5}
    }

    @classmethod
    def validate_reading(cls, raw_ec: float, soil_temp_c: float, moisture_vwc: float, battery_voltage: float = 4.0) -> Tuple[bool, List[str]]:
        """
        Returns (is_valid, list_of_anomalies)
        """
        anomalies = []

        if not (cls.LIMITS["raw_ec"]["min"] <= raw_ec <= cls.LIMITS["raw_ec"]["max"]):
            anomalies.append(f"Electrical conductivity {raw_ec} dS/m out of bounds [0, 20]")

        if not (cls.LIMITS["soil_temp_c"]["min"] <= soil_temp_c <= cls.LIMITS["soil_temp_c"]["max"]):
            anomalies.append(f"Soil temperature {soil_temp_c}°C out of bounds [-10, 65]")

        if not (cls.LIMITS["moisture_vwc"]["min"] <= moisture_vwc <= cls.LIMITS["moisture_vwc"]["max"]):
            anomalies.append(f"Soil moisture {moisture_vwc}% out of bounds [0, 100]")

        if not (cls.LIMITS["battery_voltage"]["min"] <= battery_voltage <= cls.LIMITS["battery_voltage"]["max"]):
            anomalies.append(f"Battery voltage {battery_voltage}V indicates power rail anomaly")

        return len(anomalies) == 0, anomalies
