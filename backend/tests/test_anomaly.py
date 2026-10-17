"""
Unit tests for Sensor Anomaly Detector
"""

import unittest
from app.services.anomaly_detector import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    def test_normal_reading_passes(self):
        valid, errors = AnomalyDetector.validate_reading(
            raw_ec=1.5,
            soil_temp_c=25.0,
            moisture_vwc=35.0,
            battery_voltage=4.0
        )
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)

    def test_extreme_ec_rejected(self):
        valid, errors = AnomalyDetector.validate_reading(
            raw_ec=25.0, # Impossible in normal soils
            soil_temp_c=25.0,
            moisture_vwc=35.0
        )
        self.assertFalse(valid)
        self.assertTrue(any("conductivity" in e for e in errors))

    def test_negative_temperature_or_extreme_heat_rejected(self):
        valid, errors = AnomalyDetector.validate_reading(
            raw_ec=1.5,
            soil_temp_c=80.0,
            moisture_vwc=35.0
        )
        self.assertFalse(valid)
        self.assertTrue(any("temperature" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
