# 🔌 Zerthiva — Hardware Pinout, Schematic & BOM

This document provides the complete hardware wiring diagram, Bill of Materials (BOM), and laboratory calibration protocols for the **Zerthiva Edge Field Node**.

---

## 1. Bill of Materials (BOM) Cost Breakdown

Target unit production cost: **$30.00 – $35.00** per node (at 100-unit batch volume).

| Component | Description | Model / Spec | Est. Unit Cost ($) | Source |
| :--- | :--- | :--- | :---: | :--- |
| **Microcontroller** | Dual-core 240MHz, 520KB SRAM, WiFi/BLE | ESP32-WROOM-32 DevKit V1 | $4.50 | Espressif / Local Distributor |
| **Salinity Probe** | Dual-prong analog EC probe + conditioning board | DFRobot / Gravity Analog EC v2 | $8.00 | Electronic Components Supplier |
| **Moisture Probe** | Corrosion-resistant capacitive dielectric probe | Capacitive Moisture Sensor v1.2 | $2.80 | Standard Hardware Stock |
| **Temperature Probe**| Waterproof stainless-steel 1-Wire probe | Maxim DS18B20 (-55°C to +125°C) | $1.80 | Standard Hardware Stock |
| **Cellular Modem** | Quad-band 850/900/1800/1900MHz GPRS/SMS | SIMCOM SIM800L Module | $4.80 | Standard Hardware Stock |
| **Local Storage** | MicroSD SPI Card Reader Module | Standard SPI SD Breakout | $0.90 | Standard Hardware Stock |
| **Memory Card** | 8GB or 16GB MicroSD Card (Industrial grade) | SanDisk Ultra / Kingston | $2.50 | Standard Hardware Stock |
| **Visual Sentry** | Common-cathode tri-color high-intensity LED | 5mm Diffused RGB LED | $0.20 | Standard Hardware Stock |
| **Solar Panel** | Monocrystalline solar PV panel (6V / 5W) | 165mm x 165mm Weatherproof | $4.00 | Solar Equipment Supplier |
| **Battery Storage** | 3.7V 2,200mAh Li-ion rechargeable cell | 18650 Protected Cell | $2.50 | Battery Supplier |
| **Power Controller**| Li-ion charging board with over-discharge cut | TP4056 + DW01 Protection | $0.60 | Standard Hardware Stock |
| **Enclosure** | Weatherproof IP65 junction enclosure | 120 x 80 x 65mm ABS box | $2.50 | Enclosure Manufacturer |
| **Cables & Hardware**| Cable glands (PG7), 4.7k resistor, stake mount | Misc Hardware | $1.50 | Local Hardware Store |
| **Total BOM Cost** | | | **$36.60** | *(Scale to $29.80 at 1,000 units)* |

---

## 2. ESP32 Pin Allocation Map

```text
+-----------------------+--------------------+----------------------------------------+
| ESP32 Pin Name        | Function / Module  | Wiring Description                    |
+-----------------------+--------------------+----------------------------------------+
| GPIO 34 (ADC1_CH6)    | Analog EC Probe    | Connects to Op-Amp conditioned EC Vout |
| GPIO 35 (ADC1_CH7)    | Capacitive Moist   | Connects to Analog VWC dielectric Vout |
| GPIO 32 (ADC1_CH4)    | Battery Voltage    | Connects to 100kΩ/100kΩ Divider (2:1)  |
| GPIO 4  (Digital I/O) | DS18B20 Temp Bus   | 1-Wire Data line (4.7kΩ pullup to 3.3V)|
| GPIO 14 (Digital OUT) | Power Rail Switch  | High-side P-MOSFET gate (Sensors VCC)  |
| GPIO 25 (PWM OUT)     | RGB LED - RED      | 220Ω resistor to Red Anode             |
| GPIO 26 (PWM OUT)     | RGB LED - GREEN    | 220Ω resistor to Green Anode           |
| GPIO 27 (PWM OUT)     | RGB LED - BLUE     | 220Ω resistor to Blue Anode            |
| GPIO 5  (SPI CS)      | MicroSD Card       | Chip Select (CS)                       |
| GPIO 23 (SPI MOSI)    | MicroSD Card       | Master Out Slave In (MOSI)             |
| GPIO 19 (SPI MISO)    | MicroSD Card       | Master In Slave Out (MISO)             |
| GPIO 18 (SPI SCK)     | MicroSD Card       | Serial Clock (SCK)                     |
| GPIO 17 (UART2 TX)    | SIM800L Modem      | ESP32 TX -> SIM800L RXD                |
| GPIO 16 (UART2 RX)    | SIM800L Modem      | ESP32 RX <- SIM800L TXD                |
| GPIO 15 (Digital OUT) | SIM800L Power Key  | Modem Power On / Hard Reset            |
| 3.3V                  | Logic VCC          | Power for ESP32 and MicroSD SPI bus    |
| GND                   | Common Ground      | Common ground across all modules       |
+-----------------------+--------------------+----------------------------------------+
```

---

## 3. Power Optimization & Battery Life Calculation

- **Active Measurement Mode (15 seconds per cycle):**
  - Sensors powered via GPIO14 MOSFET: $45\text{ mA}$
  - ESP32 active processing: $80\text{ mA}$
  - Total active current: $\approx 125\text{ mA}$
  - Duration: $15\text{ sec}$ ($0.0042\text{ hours}$)

- **Deep Sleep Mode (885 seconds per cycle):**
  - ESP32 RTC timer: $0.015\text{ mA}$ ($15\text{ µA}$)
  - Sensors powered down: $0.000\text{ mA}$
  - Duration: $14.75\text{ minutes}$ ($0.2458\text{ hours}$)

- **Cellular Transmission Mode (Once per 4 hours or upon Critical Alert):**
  - SIM800L GPRS burst: $250\text{ mA}$ average for $20\text{ seconds}$.

- **Net Energy Consumption:**
  $$\bar{I}_{\text{average}} \approx \frac{(125\text{ mA} \times 15\text{ s}) + (0.015\text{ mA} \times 885\text{ s})}{900\text{ s}} \approx 2.10\text{ mA}$$

- **Battery Autonomy without Solar:**
  $$\text{Runtime} = \frac{2,200\text{ mAh} \times 0.85}{2.10\text{ mA}} \approx 890\text{ hours} \approx 37\text{ days}$$
  *Even with zero sunlight during monsoon or cloudy seasons, the 2,200mAh Li-ion battery sustains node operation for over a month.*

---

## 4. Laboratory Sensor Calibration Protocol

### 4.1 Electrical Conductivity (EC) Probe Calibration
1. Prepare standard laboratory potassium chloride ($\text{KCl}$) calibration solution: $1,413\text{ µS/cm}$ ($1.413\text{ dS/m}$) at $25.0^\circ\text{C}$.
2. Submerge the probe prongs into the solution and allow temperature equilibration for 60 seconds.
3. Read the raw ADC voltage $V_{\text{raw}}$.
4. Calculate calibration constant:
   $$K = \frac{1.413}{V_{\text{raw}}}$$
5. Update `EC_CALIBRATION_K` in `firmware/src/config.py`.

### 4.2 Capacitive Moisture Probe Calibration
1. **Dry Air Baseline (0% VWC):** Suspend probe in ambient air away from metal objects. Record raw ADC value (typically $\approx 3,100$). Update `MOISTURE_AIR_RAW`.
2. **Saturation Baseline (100% VWC):** Submerge probe up to top white line in fresh water. Record raw ADC value (typically $\approx 1,400$). Update `MOISTURE_WATER_RAW`.
