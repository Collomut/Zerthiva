"""
Zerthiva WiFi Uplink Client
Used for lab bench testing, firmware staging, and farm sites with local WiFi coverage.
"""

import time
import json

try:
    import network
    import urequests
except ImportError:
    network = None
    urequests = None


class WiFiClient:
    def __init__(self, ssid: str = "", password: str = ""):
        self.ssid = ssid
        self.password = password
        self.wlan = None

        if network:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)

    def connect(self, timeout_sec: int = 15) -> bool:
        """Connects to local WiFi Access Point"""
        if not self.wlan:
            return True

        if not self.wlan.isconnected():
            self.wlan.connect(self.ssid, self.password)
            start = time.time()
            while not self.wlan.isconnected():
                if time.time() - start > timeout_sec:
                    return False
                time.sleep(0.5)
        return True

    def post_telemetry(self, endpoint_url: str, device_psk: str, payload_dict: dict) -> bool:
        """Posts telemetry data over WiFi via urequests"""
        if not self.wlan:
            return True

        headers = {
            "Content-Type": "application/json",
            "X-Device-PSK": device_psk
        }
        try:
            res = urequests.post(endpoint_url, data=json.dumps(payload_dict), headers=headers)
            status = res.status_code
            res.close()
            return status in [200, 201]
        except Exception as e:
            print("WiFi HTTP POST failed:", e)
            return False

    def disconnect(self):
        """Disconnects and puts WiFi radio into sleep mode"""
        if self.wlan and self.wlan.isconnected():
            self.wlan.disconnect()
            self.wlan.active(False)
