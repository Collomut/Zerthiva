"""
Zerthiva Electrical Conductivity (EC / TDS) Sensor Driver
Handles analog-to-digital conversion and 25°C baseline temperature compensation.
"""

try:
    from machine import ADC, Pin
except ImportError:
    # Desktop mock fallback for unit tests and local simulation
    ADC = None
    Pin = None


class ECSensor:
    def __init__(self, pin_adc: int = 34, calibration_k: float = 1.85, alpha: float = 0.020):
        """
        :param pin_adc: GPIO pin connected to analog EC probe op-amp output
        :param calibration_k: Scaling factor converting analog voltage (V) to EC (dS/m)
        :param alpha: Temperature compensation coefficient (default 0.020 = 2.0%/°C)
        """
        self.pin_num = pin_adc
        self.k = calibration_k
        self.alpha = alpha

        if ADC and Pin:
            self.adc = ADC(Pin(self.pin_num))
            self.adc.atten(ADC.ATTN_11DB)  # Full range ~0 - 3.3V
            self.adc.width(ADC.WIDTH_12BIT) # 12-bit resolution: 0 - 4095
        else:
            self.adc = None

    def read_raw_voltage(self) -> float:
        """Reads analog voltage from 12-bit ADC (3.3V Vref)"""
        if self.adc:
            raw_value = self.adc.read()
            # 12-bit ADC gives values from 0 to 4095
            voltage = (raw_value / 4095.0) * 3.3
            return round(voltage, 3)
        return 0.85 # Default mock voltage if running off-chip

    def calculate_raw_ec(self, voltage: float) -> float:
        """Converts probe voltage to raw electrical conductivity (dS/m)"""
        raw_ec = voltage * self.k
        return round(max(0.0, raw_ec), 3)

    def normalize_temperature(self, raw_ec: float, temp_c: float) -> float:
        """
        Normalizes electrical conductivity to standard 25°C baseline.
        Formula: EC_25 = EC_raw / (1 + alpha * (T - 25))
        """
        temp_factor = 1.0 + self.alpha * (temp_c - 25.0)
        if temp_factor <= 0.1:
            temp_factor = 0.1
        normalized = raw_ec / temp_factor
        return round(max(0.0, normalized), 2)

    def read(self, temp_c: float = 25.0) -> dict:
        """
        Executes an EC measurement with temperature compensation.
        :param temp_c: Current soil temperature from DS18B20 probe
        :return: Dict containing voltage, raw_ec, and normalized_ec_25
        """
        voltage = self.read_raw_voltage()
        raw_ec = self.calculate_raw_ec(voltage)
        ec_25 = self.normalize_temperature(raw_ec, temp_c)

        return {
            "voltage_v": voltage,
            "raw_ec": raw_ec,
            "normalized_ec_25": ec_25
        }
