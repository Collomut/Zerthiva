"""
SoilGuard DS18B20 Digital Temperature Sensor Driver
Uses MicroPython onewire and ds18x20 protocol to query digital soil temperature.
"""

import time

try:
    import machine
    import onewire
    import ds18x20
except ImportError:
    machine = None
    onewire = None
    ds18x20 = None


class TemperatureSensor:
    def __init__(self, pin_onewire: int = 4):
        """
        :param pin_onewire: GPIO pin connected to DS18B20 1-Wire data bus
        """
        self.pin_num = pin_onewire
        self.ds_sensor = None
        self.roms = []

        if machine and onewire and ds18x20:
            try:
                ow = onewire.OneWire(machine.Pin(self.pin_num))
                self.ds_sensor = ds18x20.DS18X20(ow)
                self.roms = self.ds_sensor.scan()
            except Exception as e:
                print("DS18B20 init warning:", e)
                self.ds_sensor = None

    def read_celsius(self) -> float:
        """Reads soil temperature in Celsius with 750ms ADC conversion delay"""
        if self.ds_sensor and self.roms:
            try:
                self.ds_sensor.convert_temp()
                time.sleep_ms(750) # Conversion time for 12-bit DS18B20
                for rom in self.roms:
                    temp = self.ds_sensor.read_temp(rom)
                    if -40.0 <= temp <= 85.0:
                        return round(temp, 1)
            except Exception as e:
                print("DS18B20 read error:", e)
        return 24.5 # Default baseline soil temperature for desktop testing
