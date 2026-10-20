"""
Zerthiva Tri-Color Visual Sentry LED Controller
Drives Common-Cathode RGB LED to communicate soil state to farmers without text or smartphone.
"""

try:
    from machine import Pin
except ImportError:
    Pin = None


class LEDController:
    def __init__(self, pin_red: int = 25, pin_green: int = 26, pin_blue: int = 27):
        self.pin_red_num = pin_red
        self.pin_green_num = pin_green
        self.pin_blue_num = pin_blue

        if Pin:
            self.r = Pin(self.pin_red_num, Pin.OUT)
            self.g = Pin(self.pin_green_num, Pin.OUT)
            self.b = Pin(self.pin_blue_num, Pin.OUT)
            self.off()
        else:
            self.r = None
            self.g = None
            self.b = None

        self.current_color = "OFF"

    def off(self):
        """Turns all LEDs off to save battery power"""
        if self.r and self.g and self.b:
            self.r.value(0)
            self.g.value(0)
            self.b.value(0)
        self.current_color = "OFF"

    def set_color(self, color_name: str):
        """
        Sets beacon color:
        - GREEN:  Optimal balance
        - YELLOW: Action required (Irrigate or Caution) - Red + Green
        - RED:    Critical salinity alert
        - BLUE:   Cellular/WiFi transmission active
        """
        color = color_name.upper().strip()
        self.off()

        if not (self.r and self.g and self.b):
            self.current_color = color
            return

        if color == "GREEN":
            self.g.value(1)
        elif color == "YELLOW":
            self.r.value(1)
            self.g.value(1)
        elif color == "RED":
            self.r.value(1)
        elif color == "BLUE":
            self.b.value(1)

        self.current_color = color
