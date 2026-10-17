"""
SoilGuard Field Telemetry Simulator
Generates diurnal temperature cycles, soil moisture depletion curves,
periodic irrigation pulses, and gradual salt accumulation over a 30-day crop lifecycle.
"""

import time
import math
import random
from typing import Dict, Any


class MockFieldNode:
    def __init__(self, device_id: str = "SG-NODE-001", crop: str = "tomato", base_ec: float = 1.2):
        self.device_id = device_id
        self.crop = crop
        self.base_ec = base_ec
        self.current_day = 1
        self.current_hour = 6
        self.battery_voltage = 4.15

    def step(self, hour_increment: int = 1) -> Dict[str, Any]:
        """
        Advances simulated clock and generates next telemetry data point.
        """
        self.current_hour = (self.current_hour + hour_increment) % 24
        if self.current_hour < hour_increment:
            self.current_day += 1

        # 1. Diurnal Temperature Curve: Peak at 14:00 (30°C), minimum at 04:00 (16°C)
        temp_c = 22.0 + 7.5 * math.sin((self.current_hour - 8) * math.pi / 12) + random.uniform(-0.4, 0.4)

        # 2. Moisture dynamics:
        # Morning irrigation at 06:00 boosts moisture by 12%
        # Evaporative loss during hot midday hours (10:00 - 16:00)
        base_moisture = 34.0 - (self.current_hour * 0.35)
        if self.current_hour == 6:
            base_moisture += 12.0
        elif 10 <= self.current_hour <= 15:
            base_moisture -= random.uniform(1.0, 2.5)

        moisture = max(18.0, min(base_moisture + random.uniform(-0.5, 0.5), 45.0))

        # 3. Progressive salt buildup:
        # Every day of continuous irrigation without leaching adds ~0.045 dS/m
        salt_buildup = (self.current_day * 0.048) + random.uniform(-0.03, 0.03)
        raw_ec = self.base_ec + salt_buildup

        # 4. Battery solar charge during day, slow drain at night
        if 8 <= self.current_hour <= 17:
            self.battery_voltage = min(4.20, self.battery_voltage + 0.02)
        else:
            self.battery_voltage = max(3.60, self.battery_voltage - 0.01)

        return {
            "device_id": self.device_id,
            "crop_name": self.crop,
            "timestamp": int(time.time()),
            "day": self.current_day,
            "hour": self.current_hour,
            "soil_temp_c": round(temp_c, 1),
            "moisture_vwc": round(moisture, 1),
            "raw_ec": round(raw_ec, 2),
            "battery_voltage": round(self.battery_voltage, 2)
        }
