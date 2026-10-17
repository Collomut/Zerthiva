# 🌊 SoilGuard — Data Flow Diagrams (DFD)

This document formalizes the data flow pathways across the **SoilGuard Soil Intelligence System (SIS)** at Level 0 (System Context) and Level 1 (Subsystem Decomposition).

---

## 1. DFD Level 0: System Context Diagram

The Level 0 diagram outlines the boundary between the physical environment, edge sensor hardware, agricultural end users, and the cloud advisory gateway:

```mermaid
flowchart TD
    subgraph Environment ["Field Soil & Microclimate"]
        SOIL[("Field Soil & Crop Root Zone\n(-20cm Depth)")]
    end

    subgraph EdgeDevice ["SoilGuard Edge Node (Field Installed)"]
        NODE["ESP32 Microcontroller\n+ Multi-Sensor Probes\n+ Local FAO Decision Engine"]
    end

    subgraph Users ["Agricultural End Users"]
        FARMER["👨‍🌾 Smallholder Farmer\n(Zero Literacy / Feature Phone)"]
        OFFICER["🧑‍💼 Extension Officer / Agronomist\n(Smartphone / Web Browser)"]
    end

    subgraph Cloud ["SoilGuard Cloud Infrastructure"]
        BACKEND["FastAPI Gateway\n+ TimescaleDB Database\n+ SMS Engine"]
    end

    SOIL -->|"Physical Properties\n(Electrical Conductivity, Moisture, Temp)"| NODE
    NODE -->|"Visual Status Pulse\n(Green / Yellow / Red LED)"| FARMER
    NODE -->|"Lightweight JSON Telemetry\n(via GSM/GPRS Cellular)"| BACKEND
    BACKEND -->|"Actionable Advisory SMS\n('Hold Fertilizer, Flush 45m')"| FARMER
    BACKEND -->|"Aggregated Regional Telemetry\n& Historical EC Curves"| OFFICER
    FARMER -->|"Closed-Loop Action\n(Irrigate, Flush Salts, Apply Fertilizer)"| SOIL
```

---

## 2. DFD Level 1: Subsystem Data Flow Decomposition

The Level 1 diagram breaks down internal data flow transformations from raw sensor ADC voltages to normalized agronomic metrics, local persistence, LED modulation, and cloud analytics:

```mermaid
flowchart TD
    %% Sensors to Edge Engine
    S_EC["Analog EC Sensor Probe"] -->|"Analog Voltage (ADC)"| P1["1.0 Sensor Acquisition\n& ADC Calibration"]
    S_MOIST["Capacitive Moisture Probe"] -->|"Dielectric Voltage (ADC)"| P1
    S_TEMP["DS18B20 Temp Probe"] -->|"1-Wire Digital Signal"| P1

    P1 -->|"Raw Values (V_ec, V_moist, T_celsius)"| P2["2.0 Temperature Normalization\n& Metric Conditioning"]
    
    P2 -->|"Normalized EC_25 (dS/m)\nVolumetric Moisture (%)\nTemp (°C)"| D1[("Local 7-Day Rolling Log\n(MicroSD Card SPI)")]
    P2 -->|"Current Field Vector"| P3["3.0 Agronomic Decision Engine\n(FAO-56 Threshold Evaluator)"]

    %% Decision Engine Logic
    D2[("FAO Crop Threshold Table\n(EC_max, Field Capacity)")] -->|"Crop Tolerances"| P3
    
    P3 -->|"Action Level (SAFE / CAUTION / CRITICAL)\nLeaching Requirement (LR)"| P4["4.0 Local Alert Dispatcher"]
    
    P4 -->|"RGB Pin PWM Modulation"| LED["Tri-Color Status Beacon"]
    P4 -->|"Formatted SMS String"| GSM["SIM800L GSM Module"]
    
    GSM -->|"Cellular SMS Payload"| FARMER_PHONE["Farmer Nokia / Feature Phone"]
    GSM -->|"HTTP POST /telemetry"| CLOUD_API["FastAPI Cloud Gateway"]
    
    CLOUD_API -->|"Validate & Store"| TIMESCALE[("TimescaleDB\nTelemetry Hypertable")]
    TIMESCALE -->|"REST Endpoints"| DASHBOARD["React Agronomic Web Dashboard"]
```

---

## 3. Data Dictionary

| Data Element | Type | Units | Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `raw_ec` | Float | dS/m | 0.0 – 20.0 | Measured soil water electrical conductivity before temperature correction. |
| `normalized_ec_25` | Float | dS/m | 0.0 – 20.0 | Electrical conductivity normalized to 25°C baseline using $\alpha = 0.020$/°C. |
| `moisture_vwc` | Float | % VWC | 0.0 – 100.0 | Volumetric Water Content percentage derived from capacitive dielectric frequency. |
| `soil_temp_c` | Float | °C | -10.0 – 65.0 | Soil temperature at -20cm root zone depth measured by DS18B20. |
| `status` | String | Enum | OPTIMAL, IRRIGATE, CAUTION, CRITICAL | Core agronomic state classification. |
| `action` | String | Enum | NONE, WATER_FIELD, PAUSE_WATER, FLUSH_SALTS | Direct physical task commanded to farmer. |
| `allow_fertilizer` | Boolean | Flag | True / False | Chemical lockout preventing fertilizer burn during elevated salinity. |
| `leaching_fraction` | Float | Fraction | 0.05 – 0.45 | Fraction of extra irrigation water required to leach salts below root zone. |
