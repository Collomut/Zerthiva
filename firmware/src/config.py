"""
Zerthiva Edge Firmware Configuration
Hardware Pinout, Agronomic Constants, and Sensor Calibration Parameters
"""

# Device Identity
DEVICE_ID = "SG-NODE-001"
FIRMWARE_VERSION = "1.0.0"

# ESP32 Pinout Mapping
PIN_EC_ADC = 34          # ADC1_CH6: Analog EC Sensor Output
PIN_MOISTURE_ADC = 35    # ADC1_CH7: Capacitive Moisture Sensor Output
PIN_BATTERY_ADC = 32     # ADC1_CH4: Battery Voltage Divider (100k / 100k)
PIN_TEMP_ONEWIRE = 4     # GPIO4: DS18B20 Digital 1-Wire Bus (with 4.7k pullup)
PIN_SENSOR_POWER = 14    # GPIO14: High-Side P-MOSFET / N-MOSFET Sensor Power Rail

# Tri-Color Status Beacon (Common Cathode)
PIN_LED_RED = 25         # GPIO25: Critical Salinity Warning
PIN_LED_GREEN = 26       # GPIO26: Optimal Balance
PIN_LED_BLUE = 27        # GPIO27: Comms / Activity Indicator

# MicroSD SPI Bus
PIN_SD_CS = 5            # GPIO5: SPI Chip Select
PIN_SD_MOSI = 23         # GPIO23: SPI Master Out Slave In
PIN_SD_MISO = 19         # GPIO19: SPI Master In Slave Out
PIN_SD_SCK = 18          # GPIO18: SPI Clock

# SIM800L Cellular Modem (UART2)
PIN_GSM_TX = 17          # GPIO17: ESP32 TX -> SIM800L RXD
PIN_GSM_RX = 16          # GPIO16: ESP32 RX <- SIM800L TXD
PIN_GSM_PWR = 15         # GPIO15: Modem Power Key / Reset
GSM_BAUDRATE = 9600

# Sensor Calibration Constants
# EC Calibration: standard K factor for 0-3.3V analog output (dS/m per Volt)
EC_CALIBRATION_K = 1.85
EC_TEMP_ALPHA = 0.020    # 2.0% per °C standard temperature coefficient

# Capacitive Moisture Sensor Calibration (12-bit ADC: 0 - 4095)
# In dry air: ADC ~ 3100 (0% VWC), In pure water: ADC ~ 1400 (100% VWC equivalent)
MOISTURE_AIR_RAW = 3100
MOISTURE_WATER_RAW = 1400

# Battery Measurement (Li-ion 3.0V - 4.2V, 2:1 voltage divider)
BATTERY_DIVIDER_RATIO = 2.0
BATTERY_MIN_V = 3.3
BATTERY_MAX_V = 4.2

# Edge Cycle Scheduling
CYCLE_INTERVAL_SEC = 900 # 15 minutes = 900 seconds
DEEP_SLEEP_ENABLED = True
DAILY_SYNC_INTERVAL_CYCLES = 16 # Send batch to cloud every 4 hours (16 * 15m)

# Default Agronomic Baseline
DEFAULT_CROP = "maize"
DEFAULT_EC_WATER = 0.6   # Typical irrigation water salinity in dS/m
FARMER_PHONE_NUMBER = "+254700000000"

# Cloud Ingestion Endpoint (when cellular GPRS or WiFi active)
CLOUD_INGEST_URL = "http://api.zerthiva.org/api/v1/ingest/telemetry"
DEVICE_PSK = "sg-field-device-pre-shared-key-2026"
