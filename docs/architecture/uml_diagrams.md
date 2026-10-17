# 📐 SoilGuard — UML Architecture Diagrams

This document contains the complete Unified Modeling Language (UML) specifications for the **SoilGuard Soil Intelligence System (SIS)**.

---

## 1. UML Class Diagram: Domain & Edge Architecture

```mermaid
classDiagram
    class SoilSensorNode {
        +String device_id
        +String firmware_version
        +CropProfile current_crop
        +Boolean is_low_power_mode
        +initialize() void
        +read_sensors() SensorReading
        +execute_cycle() void
        +sleep(duration_sec: int) void
    }

    class SensorReading {
        +float raw_ec
        +float normalized_ec_25
        +float moisture_vwc
        +float soil_temp_c
        +int timestamp
        +to_csv() String
        +to_json() String
    }

    class ECSensor {
        +int adc_pin
        +float calibration_k
        +read_raw_voltage() float
        +calculate_ec(voltage: float, temp_c: float) float
    }

    class MoistureSensor {
        +int adc_pin
        +int air_val
        +int water_val
        +read_percentage() float
    }

    class TemperatureSensor {
        +int onewire_pin
        +read_celsius() float
    }

    class CropProfile {
        +String crop_name
        +float ec_threshold_max
        +float field_capacity_min
        +float field_capacity_max
        +int growth_stage_days
    }

    class AgronomicDecisionEngine {
        +evaluate(reading: SensorReading, crop: CropProfile) DecisionResult
        +compute_leaching_fraction(ec_water: float, ec_target: float) float
    }

    class DecisionResult {
        +String alert_level
        +String recommendation_text
        +float leaching_volume_liters
        +Boolean allow_fertilizer
    }

    SoilSensorNode "1" *-- "1" ECSensor
    SoilSensorNode "1" *-- "1" MoistureSensor
    SoilSensorNode "1" *-- "1" TemperatureSensor
    SoilSensorNode "1" *-- "1" AgronomicDecisionEngine
    SoilSensorNode "1" --> "1" CropProfile
    SoilSensorNode ..> SensorReading : generates
    AgronomicDecisionEngine ..> DecisionResult : produces
```

---

## 2. UML Sequence Diagram: 15-Minute Sensor & Decision Cycle

```mermaid
sequenceDiagram
    autonumber
    participant Timer as ESP32 RTC Wakeup
    participant Main as main.py (Orchestrator)
    participant Sensors as Multi-Sensor Subsystem
    participant Engine as Agronomic Decision Engine
    participant LED as LED Controller
    participant Storage as MicroSD SPI Logger
    participant GSM as SIM800L Module
    participant Cloud as Cloud API

    Timer->>Main: RTC Alarm triggers wake from Deep Sleep
    Main->>Sensors: Power up sensor bus (GPIO switch)
    Main->>Sensors: read_temperature()
    Sensors-->>Main: Return 24.5 °C
    Main->>Sensors: read_ec(temp=24.5)
    Sensors-->>Main: Return normalized 2.8 dS/m (High!)
    Main->>Sensors: read_moisture()
    Sensors-->>Main: Return 32% VWC
    Main->>Sensors: Power down sensor bus (Power Saving)

    Main->>Engine: evaluate(EC=2.8, Moist=32%, Crop="Tomato")
    Note over Engine: Threshold for Tomato = 2.5 dS/m.<br/>EC 2.8 exceeds safe threshold.<br/>Calculate Leaching Fraction (LR).
    Engine-->>Main: Return DecisionResult(Alert=RED, Flush=True, Fertilizer=BLOCKED)

    Main->>LED: set_state(RED_PULSE)
    Note over LED: Red pulse alerts farmer<br/>in the field immediately.

    Main->>Storage: append_csv(timestamp, 2.8, 32, 24.5, "RED")
    Storage-->>Main: Log written OK

    alt Salinity Critical or Daily Sync Due
        Main->>GSM: power_on_uart()
        Main->>GSM: send_sms(phone, "SoilGuard Alert: High salt in tomato field. Hold fertilizer. Water for 45 min extra to flush.")
        GSM-->>Main: SMS Sent OK
        Main->>GSM: http_post(endpoint="/v1/telemetry", payload=JSON)
        Cloud-->>GSM: 201 Created
        GSM->>Main: HTTP 201 OK
        Main->>GSM: power_down()
    end

    Main->>Main: Configure RTC for next 15-min interval
    Main->>Timer: Enter Deep Sleep (0.015 mA draw)
```

---

## 3. UML State Machine Diagram: Edge Firmware Lifecycle

```mermaid
stateDiagram-v2
    [*] --> DEEP_SLEEP

    DEEP_SLEEP --> WAKE_BOOT: RTC Timer Expires (15 min)
    WAKE_BOOT --> HARDWARE_INIT: Initialize GPIO, ADC & SPI

    HARDWARE_INIT --> SENSOR_POLLING: Turn On Sensor Power Rail
    state SENSOR_POLLING {
        [*] --> ReadTemperature
        ReadTemperature --> ReadMoisture
        ReadMoisture --> ReadSalinityEC
        ReadSalinityEC --> TempNormalizeEC
        TempNormalizeEC --> [*]
    }

    SENSOR_POLLING --> AGRONOMIC_EVALUATION: Power Off Sensor Rail
    
    state AGRONOMIC_EVALUATION {
        [*] --> CompareCropThresholds
        CompareCropThresholds --> SafeState: EC <= Threshold
        CompareCropThresholds --> CautionState: EC near Threshold
        CompareCropThresholds --> CriticalState: EC > Threshold
        CriticalState --> CalculateLeachingFraction: Compute Flush Volume
    }

    AGRONOMIC_EVALUATION --> LOCAL_LOGGING: Append to MicroSD CSV
    LOCAL_LOGGING --> VISUAL_ALERT: Update Tri-Color LED (Green / Yellow / Red)

    VISUAL_ALERT --> COMMS_DISPATCH: Alert == CRITICAL or Time == SyncHour
    VISUAL_ALERT --> PREPARE_SLEEP: Alert == SAFE and No Sync Required

    state COMMS_DISPATCH {
        [*] --> PowerOnModem
        PowerOnModem --> DispatchSMS: If Critical Alert
        DispatchSMS --> TransmitCloudJSON: Send Telemetry
        TransmitCloudJSON --> PowerOffModem
        PowerOffModem --> [*]
    }

    COMMS_DISPATCH --> PREPARE_SLEEP
    PREPARE_SLEEP --> DEEP_SLEEP: Enter Low-Power Standby
```

---

## 4. UML Deployment Diagram: Physical & Cloud Infrastructure

```mermaid
flowchart TB
    subgraph FarmSite ["Physical Farm Site (Sub-Saharan Africa)"]
        subgraph Enclosure ["IP65 Weatherproof Node Enclosure"]
            MCU["ESP32 Microcontroller (Firmware v1.0)"]
            PWR["TP4056 + 2200mAh LiPo + 5W Solar"]
            MODEM["SIM800L Quad-Band GSM Module"]
            SD["MicroSD SPI Storage Card"]
            LED_DEV["Tri-Color High-Intensity LED"]
        end

        subgraph Probes ["Soil Insertion Zone (-20cm Depth)"]
            P_EC["Dual-Prong Analog EC Sensor"]
            P_MOIST["Capacitive Dielectric Moisture Sensor"]
            P_TEMP["Waterproof DS18B20 Temp Probe"]
        end

        Probes -->|Analog / 1-Wire Cable| Enclosure
    end

    subgraph CellularNetwork ["Telecom Infrastructure"]
        BTS["Cell Tower / 2G-3G GPRS BTS"]
        SMSC["Carrier SMSC Gateway"]
    end

    subgraph FarmerDevice ["Farmer End Device"]
        PHONE["Basic Feature Phone\n(Nokia 105, etc.)"]
    end

    subgraph CloudVPC ["Cloud Hosting Environment (VPS / AWS Lightsail)"]
        NGINX["Nginx Reverse Proxy + SSL / TLS 1.3"]
        FASTAPI["FastAPI Python 3.10 Service (Docker)"]
        POSTGRES[("TimescaleDB PostgreSQL (Docker)")]
        WEB_APP["React Web Dashboard (Nginx Static)"]
    end

    subgraph OfficerDevice ["Extension Officer Device"]
        PC["Laptop / Smartphone Browser"]
    end

    MODEM -->|Radio RF| BTS
    BTS -->|SMPP Protocol| SMSC
    SMSC -->|Cellular SMS| PHONE
    BTS -->|TCP/IP GPRS| NGINX

    NGINX --> FASTAPI
    FASTAPI --> POSTGRES
    FASTAPI --> WEB_APP
    WEB_APP -->|HTTPS| PC
```
