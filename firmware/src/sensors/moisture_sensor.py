"""
Zerthiva Capacitive Soil Moisture Sensor Driver
Translates dielectric capacitance readings into Volumetric Water Content percentage (VWC%).
"""

try:
    from machine import ADC, Pin
except ImportError:
    ADC = None
    Pin = None


class MoistureSensor:
    def __init__(self, pin_adc: int = 35, air_val: int = 3100, water_val: int = 1400):
        """
        :param pin_adc: GPIO pin connected to analog capacitive sensor
        :param air_val: ADC reading in dry air (0% VWC calibration baseline)
        :param water_val: ADC reading in water (100% saturation calibration baseline)
        """
        self.pin_num = pin_adc
        self.air_val = air_val
        self.water_val = water_val

        if ADC and Pin:
            self.adc = ADC(Pin(self.pin_num))
            self.adc.atten(ADC.ATTN_11DB)
            self.adc.width(ADC.WIDTH_12BIT)
        else:
            self.adc = None

    def read_raw_adc(self) -> int:
        """Returns raw 12-bit ADC value (0 - 4095)"""
        if self.adc:
            return self.adc.read()
        return 2250 # Mock value (mid-range ~50%)

    def calculate_vwc_percent(self, raw_adc: int) -> float:
        """
        Calculates Volumetric Water Content percentage (VWC%)
        Higher ADC reading = lower moisture (capacitive inverted response)
        """
        span = self.air_val - self.water_val
        if span <= 0:
            return 0.0

        # Invert relationship: air_val is dry (0%), water_val is saturated (100%)
        vwc = ((self.air_val - raw_adc) / span) * 100.0
        return round(min(max(vwc, 0.0), 100.0), 1)

    def read(self) -> dict:
        """Performs a soil moisture reading"""
        raw_adc = self.read_raw_adc()
        vwc_percent = self.calculate_vwc_percent(raw_adc)

        return {
            "raw_adc": raw_adc,
            "moisture_vwc": vwc_percent
        }
