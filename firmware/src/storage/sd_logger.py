"""
Zerthiva MicroSD Storage Driver & Rolling CSV Logger
Stores timestamped field telemetry locally for offline auditing and field technician readout.
"""

import os
import time

try:
    import machine
    import uos
    import sdcard
except ImportError:
    machine = None
    uos = None
    sdcard = None


class SDLogger:
    def __init__(self, cs_pin: int = 5, mosi: int = 23, miso: int = 19, sck: int = 18, mount_point: str = "/sd"):
        self.mount_point = mount_point
        self.is_mounted = False
        self.csv_path = f"{mount_point}/zerthiva_telemetry.csv"

        if machine and uos and sdcard:
            try:
                spi = machine.SPI(1, baudrate=10000000, polarity=0, phase=0,
                                  sck=machine.Pin(sck), mosi=machine.Pin(mosi), miso=machine.Pin(miso))
                sd = sdcard.SDCard(spi, machine.Pin(cs_pin))
                uos.mount(sd, self.mount_point)
                self.is_mounted = True
                print(f"MicroSD mounted at {self.mount_point}")
            except Exception as e:
                print(f"MicroSD mount warning: {e}. Falling back to internal flash.")
                self.csv_path = "/zerthiva_telemetry.csv"
        else:
            # Desktop fallback path
            self.csv_path = "zerthiva_telemetry.csv"

        self._ensure_header()

    def _ensure_header(self):
        """Creates CSV file with appropriate column headers if not present"""
        try:
            needs_header = False
            try:
                size = os.stat(self.csv_path)[6]
                if size == 0:
                    needs_header = True
            except OSError:
                needs_header = True

            if needs_header:
                with open(self.csv_path, "a") as f:
                    f.write("timestamp,raw_ec,normalized_ec_25,moisture_vwc,soil_temp_c,status,action,allow_fertilizer\n")
        except Exception as e:
            print("Failed to initialize CSV header:", e)

    def log_reading(self, timestamp: int, raw_ec: float, ec_25: float, moisture_vwc: float,
                    temp_c: float, status: str, action: str, allow_fertilizer: bool) -> bool:
        """Appends a 15-minute telemetry point to CSV"""
        try:
            line = f"{timestamp},{raw_ec:.3f},{ec_25:.2f},{moisture_vwc:.1f},{temp_c:.1f},{status},{action},{int(allow_fertilizer)}\n"
            with open(self.csv_path, "a") as f:
                f.write(line)
            return True
        except Exception as e:
            print("SD Logger write error:", e)
            return False

    def read_recent_logs(self, limit: int = 20) -> list:
        """Reads latest N telemetry records for diagnostics"""
        records = []
        try:
            with open(self.csv_path, "r") as f:
                lines = f.readlines()
                # Skip header
                data_lines = lines[1:] if len(lines) > 1 else []
                for line in data_lines[-limit:]:
                    records.append(line.strip().split(","))
        except Exception as e:
            print("Error reading logs:", e)
        return records
