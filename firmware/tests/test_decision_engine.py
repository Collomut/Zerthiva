"""
Unit tests for the Zerthiva Agronomic Decision Engine (FAO-56)
"""

import unittest
from firmware.src.engine.decision_engine import DecisionEngine
from firmware.src.engine.fao_tables import CROP_PROFILES, get_crop_profile


class TestAgronomicDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DecisionEngine(ec_water_source=0.6)

    def test_crop_profiles_exist(self):
        self.assertIn("maize", CROP_PROFILES)
        self.assertIn("tomato", CROP_PROFILES)
        self.assertIn("rice", CROP_PROFILES)
        self.assertIn("wheat", CROP_PROFILES)

        maize = get_crop_profile("maize")
        self.assertEqual(maize["threshold_ec"], 1.7)
        self.assertEqual(maize["slope_percent"], 12.0)

    def test_optimal_equilibrium(self):
        # EC 1.2 dS/m (below 1.7), Moisture 30% (between 22% and 38%), Temp 25°C
        res = self.engine.evaluate("maize", raw_ec=1.2, temp_c=25.0, moisture_vwc=30.0)
        self.assertEqual(res["status"], "OPTIMAL")
        self.assertEqual(res["led_color"], "GREEN")
        self.assertEqual(res["action"], "NONE")
        self.assertTrue(res["allow_fertilizer"])
        self.assertEqual(res["projected_yield_loss_percent"], 0.0)

    def test_critical_salinity_triggers_flush_and_fertilizer_lockout(self):
        # EC 2.8 dS/m (exceeds maize threshold of 1.7 dS/m)
        res = self.engine.evaluate("maize", raw_ec=2.8, temp_c=25.0, moisture_vwc=28.0)
        self.assertEqual(res["status"], "CRITICAL")
        self.assertEqual(res["led_color"], "RED")
        self.assertEqual(res["action"], "FLUSH_SALTS")
        self.assertFalse(res["allow_fertilizer"])
        self.assertGreater(res["leaching_fraction"], 0.05)
        self.assertGreater(res["projected_yield_loss_percent"], 0.0)
        self.assertIn("Hold fertilizer", res["sms_message"])

    def test_dry_soil_triggers_irrigation(self):
        # EC 1.1 dS/m (safe), Moisture 16% (below refill point 22%)
        res = self.engine.evaluate("maize", raw_ec=1.1, temp_c=25.0, moisture_vwc=16.0)
        self.assertEqual(res["status"], "IRRIGATE")
        self.assertEqual(res["led_color"], "YELLOW")
        self.assertEqual(res["action"], "WATER_FIELD")
        self.assertTrue(res["allow_fertilizer"])
        self.assertIn("Soil moisture is low", res["sms_message"])

    def test_waterlogged_soil_triggers_pause(self):
        # EC 1.1 dS/m (safe), Moisture 44% (above field capacity 38%)
        res = self.engine.evaluate("maize", raw_ec=1.1, temp_c=25.0, moisture_vwc=44.0)
        self.assertEqual(res["status"], "CAUTION")
        self.assertEqual(res["led_color"], "YELLOW")
        self.assertEqual(res["action"], "PAUSE_WATER")
        self.assertFalse(res["allow_fertilizer"])
        self.assertIn("Soil saturated", res["sms_message"])

    def test_leaching_requirement_calculation(self):
        # For ECw=0.6, ECe=1.7:
        # LR = 0.6 / (5 * 1.7 - 0.6) = 0.6 / 7.9 = 0.0759... -> rounded to 0.08
        lr = self.engine.calculate_leaching_requirement(ec_soil_target=1.7)
        self.assertAlmostEqual(lr, 0.08, places=2)

        # Clamping check: very high target EC
        lr_low = self.engine.calculate_leaching_requirement(ec_soil_target=10.0)
        self.assertGreaterEqual(lr_low, 0.05)

        # Clamping check: very low target EC
        lr_high = self.engine.calculate_leaching_requirement(ec_soil_target=0.3)
        self.assertLessEqual(lr_high, 0.45)

    def test_tomato_thresholds(self):
        # Tomato has 2.5 dS/m threshold
        # At 2.1 dS/m, tomato should still be OPTIMAL
        res = self.engine.evaluate("tomato", raw_ec=2.1, temp_c=25.0, moisture_vwc=32.0)
        self.assertEqual(res["status"], "OPTIMAL")

        # At 3.0 dS/m, tomato enters CRITICAL
        res_crit = self.engine.evaluate("tomato", raw_ec=3.0, temp_c=25.0, moisture_vwc=32.0)
        self.assertEqual(res_crit["status"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
