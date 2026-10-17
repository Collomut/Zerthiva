"""
Unit tests for EC temperature compensation and moisture sensor conversions
"""

import unittest
from firmware.src.sensors.ec_sensor import ECSensor
from firmware.src.sensors.moisture_sensor import MoistureSensor


class TestSensorCalibration(unittest.TestCase):
    def setUp(self):
        self.ec_sensor = ECSensor(pin_adc=34, calibration_k=1.85, alpha=0.020)
        self.moist_sensor = MoistureSensor(pin_adc=35, air_val=3100, water_val=1400)

    def test_ec_temperature_normalization_at_baseline(self):
        # At exactly 25.0°C, normalized EC must equal raw EC
        raw_ec = 2.00
        ec_25 = self.ec_sensor.normalize_temperature(raw_ec, temp_c=25.0)
        self.assertEqual(ec_25, 2.00)

    def test_ec_temperature_compensation_at_elevated_temperature(self):
        # At 35.0°C (warm tropical afternoon):
        # temp_factor = 1.0 + 0.020 * (35 - 25) = 1.20
        # normalized = 2.40 / 1.20 = 2.00
        raw_ec = 2.40
        ec_25 = self.ec_sensor.normalize_temperature(raw_ec, temp_c=35.0)
        self.assertEqual(ec_25, 2.00)

    def test_ec_temperature_compensation_at_cold_temperature(self):
        # At 15.0°C (cold morning):
        # temp_factor = 1.0 + 0.020 * (15 - 25) = 0.80
        # normalized = 1.60 / 0.80 = 2.00
        raw_ec = 1.60
        ec_25 = self.ec_sensor.normalize_temperature(raw_ec, temp_c=15.0)
        self.assertEqual(ec_25, 2.00)

    def test_moisture_vwc_air_and_water_limits(self):
        # Air reading (3100) must return 0% VWC
        self.assertEqual(self.moist_sensor.calculate_vwc_percent(3100), 0.0)

        # Water reading (1400) must return 100% VWC
        self.assertEqual(self.moist_sensor.calculate_vwc_percent(1400), 100.0)

        # Midpoint reading: (3100 + 1400) / 2 = 2250 -> 50.0% VWC
        self.assertEqual(self.moist_sensor.calculate_vwc_percent(2250), 50.0)

        # Clamp check: extreme values
        self.assertEqual(self.moist_sensor.calculate_vwc_percent(4000), 0.0)
        self.assertEqual(self.moist_sensor.calculate_vwc_percent(1000), 100.0)


if __name__ == "__main__":
    unittest.main()
