"""
Zerthiva Edge Firmware Main Orchestrator
Executes the 15-minute sensor acquisition, FAO agronomic evaluation,
local sentry actuation, MicroSD logging, and cellular alert dispatch.
"""

import time
import json

try:
    import machine
except ImportError:
    machine = None

from . import config
from .sensors.ec_sensor import ECSensor
from .sensors.moisture_sensor import MoistureSensor
from .sensors.temp_ds18b20 import TemperatureSensor
from .engine.decision_engine import DecisionEngine
from .engine.led_controller import LEDController
from .storage.sd_logger import SDLogger
from .comms.gsm_sim800 import SIM800L


class ZerthivaNode:
    def __init__(self):
        self.device_id = config.DEVICE_ID
        self.crop_name = config.DEFAULT_CROP
        self.cycle_count = 0

        # Initialize hardware abstractions
        self.ec_sensor = ECSensor(
            pin_adc=config.PIN_EC_ADC,
            calibration_k=config.EC_CALIBRATION_K,
            alpha=config.EC_TEMP_ALPHA
        )
        self.moist_sensor = MoistureSensor(
            pin_adc=config.PIN_MOISTURE_ADC,
            air_val=config.MOISTURE_AIR_RAW,
            water_val=config.MOISTURE_WATER_RAW
        )
        self.temp_sensor = TemperatureSensor(pin_onewire=config.PIN_TEMP_ONEWIRE)
        self.decision_engine = DecisionEngine(ec_water_source=config.DEFAULT_EC_WATER)
        self.led = LEDController(
            pin_red=config.PIN_LED_RED,
            pin_green=config.PIN_LED_GREEN,
            pin_blue=config.PIN_LED_BLUE
        )
        self.logger = SDLogger(
            cs_pin=config.PIN_SD_CS,
            mosi=config.PIN_SD_MOSI,
            miso=config.PIN_SD_MISO,
            sck=config.PIN_SD_SCK
        )
        self.modem = SIM800L(
            uart_id=2,
            tx_pin=config.PIN_GSM_TX,
            rx_pin=config.PIN_GSM_RX,
            pwr_pin=config.PIN_GSM_PWR,
            baudrate=config.GSM_BAUDRATE
        )

        # Sensor power rail switch
        if machine:
            self.pwr_rail = machine.Pin(config.PIN_SENSOR_POWER, machine.Pin.OUT)
            self.pwr_rail.value(0)
        else:
            self.pwr_rail = None

    def power_sensors(self, enable: bool):
        """Enables high-side MOSFET to power sensor probes during readings"""
        if self.pwr_rail:
            self.pwr_rail.value(1 if enable else 0)
        time.sleep(0.15) # Stabilization delay

    def read_battery_voltage(self) -> float:
        """Measures Li-ion battery voltage via resistor divider"""
        if machine:
            try:
                adc = machine.ADC(machine.Pin(config.PIN_BATTERY_ADC))
                adc.atten(machine.ADC.ATTN_11DB)
                raw = adc.read()
                voltage = (raw / 4095.0) * 3.3 * config.BATTERY_DIVIDER_RATIO
                return round(voltage, 2)
            except Exception:
                pass
        return 3.95 # Mock battery level in Volts

    def run_cycle(self) -> dict:
        """
        Executes a single 15-minute sense-decide-alert-log loop.
        """
        print(f"\n--- [{time.time()}] Zerthiva Cycle Begin ({self.device_id}) ---")
        self.cycle_count += 1

        # 1. Power up sensors
        self.power_sensors(True)

        # 2. Acquire sensor values
        temp_c = self.temp_sensor.read_celsius()
        ec_data = self.ec_sensor.read(temp_c=temp_c)
        raw_ec = ec_data["raw_ec"]
        ec_25 = ec_data["normalized_ec_25"]

        moist_data = self.moist_sensor.read()
        moisture_vwc = moist_data["moisture_vwc"]

        battery_v = self.read_battery_voltage()

        # 3. Power down sensors immediately to minimize corrosion and power drain
        self.power_sensors(False)

        print(f"Metrics -> Temp: {temp_c}°C | Raw EC: {raw_ec} dS/m | Normalized EC_25: {ec_25} dS/m | Moisture: {moisture_vwc}% | Battery: {battery_v}V")

        # 4. Agronomic Decision Engine Evaluation
        decision = self.decision_engine.evaluate(
            crop_name=self.crop_name,
            raw_ec=raw_ec,
            temp_c=temp_c,
            moisture_vwc=moisture_vwc
        )
        status = decision["status"]
        led_color = decision["led_color"]
        action = decision["action"]
        allow_fertilizer = decision["allow_fertilizer"]
        sms_msg = decision["sms_message"]

        print(f"Decision -> Status: {status} | Beacon: {led_color} | Action: {action} | Fertilizer Allowed: {allow_fertilizer}")
        print(f"Advisory -> {decision['summary']}")

        # 5. Actuate Visual Sentry
        self.led.set_color(led_color)

        # 6. Local MicroSD Persistence
        timestamp = int(time.time())
        self.logger.log_reading(
            timestamp=timestamp,
            raw_ec=raw_ec,
            ec_25=ec_25,
            moisture_vwc=moisture_vwc,
            temp_c=temp_c,
            status=status,
            action=action,
            allow_fertilizer=allow_fertilizer
        )

        # 7. Cellular Communication Dispatch
        is_critical = (status == "CRITICAL")
        is_sync_due = (self.cycle_count % config.DAILY_SYNC_INTERVAL_CYCLES == 0)

        if is_critical or is_sync_due:
            print("Activating Cellular Modem for alert dispatch / telemetry sync...")
            self.led.set_color("BLUE") # Indicator for cellular transmission
            self.modem.initialize()

            # Direct SMS to farmer if critical salt condition detected
            if is_critical:
                self.modem.send_sms(config.FARMER_PHONE_NUMBER, sms_msg)

            # Cloud Telemetry Uplink
            telemetry_payload = json.dumps({
                "device_id": self.device_id,
                "timestamp": timestamp,
                "crop_name": self.crop_name,
                "soil_temp_c": temp_c,
                "raw_ec": raw_ec,
                "normalized_ec_25": ec_25,
                "moisture_vwc": moisture_vwc,
                "battery_voltage": battery_v,
                "status": status,
                "action": action,
                "allow_fertilizer": allow_fertilizer,
                "leaching_fraction": decision.get("leaching_fraction", 0.0)
            })

            self.modem.http_post_telemetry(
                endpoint_url=config.CLOUD_INGEST_URL,
                device_psk=config.DEVICE_PSK,
                json_payload=telemetry_payload
            )

            self.modem.power_down()
            self.led.set_color(led_color) # Restore sentry state

        # Return execution summary
        return {
            "device_id": self.device_id,
            "timestamp": timestamp,
            "crop": self.crop_name,
            "soil_temp_c": temp_c,
            "raw_ec": raw_ec,
            "normalized_ec_25": ec_25,
            "moisture_vwc": moisture_vwc,
            "battery_voltage": battery_v,
            "decision": decision
        }

    def sleep(self, seconds: int = 900):
        """Puts ESP32 into RTC Deep Sleep to preserve battery"""
        print(f"Entering low-power standby for {seconds} seconds...")
        if machine and config.DEEP_SLEEP_ENABLED:
            machine.deepsleep(seconds * 1000)
        else:
            time.sleep(min(seconds, 2))


def main():
    node = ZerthivaNode()
    while True:
        node.run_cycle()
        node.sleep(config.CYCLE_INTERVAL_SEC)


if __name__ == "__main__":
    main()
