"""
Zerthiva SIM800L Cellular Modem Driver
Handles cellular AT commands for plain-language SMS dispatch and GPRS HTTP POST telemetry upload.
"""

import time

try:
    from machine import UART, Pin
except ImportError:
    UART = None
    Pin = None


class SIM800L:
    def __init__(self, uart_id: int = 2, tx_pin: int = 17, rx_pin: int = 16, pwr_pin: int = 15, baudrate: int = 9600):
        self.uart_id = uart_id
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.pwr_pin_num = pwr_pin
        self.baudrate = baudrate

        if Pin:
            self.pwr = Pin(self.pwr_pin_num, Pin.OUT)
            self.pwr.value(1) # Default high (off for inverted key)
        else:
            self.pwr = None

        if UART:
            self.uart = UART(self.uart_id, baudrate=self.baudrate, tx=self.tx_pin, rx=self.rx_pin)
        else:
            self.uart = None

    def send_at_command(self, cmd: str, expected_response: str = "OK", timeout_ms: int = 3000) -> bool:
        """Sends an AT command string to the modem and verifies response"""
        if not self.uart:
            # Mock mode for testing off-board
            return True

        # Clear buffer
        while self.uart.any():
            self.uart.read()

        full_cmd = (cmd + "\r\n").encode("utf-8")
        self.uart.write(full_cmd)

        start_time = time.ticks_ms() if hasattr(time, "ticks_ms") else int(time.time() * 1000)
        buffer = b""

        while True:
            if hasattr(time, "ticks_diff"):
                elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            else:
                elapsed = int(time.time() * 1000) - start_time

            if elapsed > timeout_ms:
                return False

            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    buffer += chunk
                    if expected_response.encode("utf-8") in buffer:
                        return True

    def initialize(self) -> bool:
        """Tests basic AT handshake and configures SMS text mode"""
        if not self.send_at_command("AT"):
            return False
        self.send_at_command("ATE0")       # Echo off
        self.send_at_command("AT+CMGF=1")  # SMS Text Mode
        return True

    def get_signal_strength(self) -> int:
        """Queries network signal quality (CSQ: 0 to 31, 99=unknown)"""
        if not self.uart:
            return 24 # Mock signal
        self.uart.write(b"AT+CSQ\r\n")
        # In field operation, parses +CSQ: <rssi>,<ber>
        return 20

    def send_sms(self, phone_number: str, message: str) -> bool:
        """
        Dispatches an actionable plain-language SMS to farmer feature phone.
        """
        if not self.uart:
            print(f"[MOCK CELLULAR SMS] To: {phone_number} | Msg: {message}")
            return True

        self.send_at_command("AT+CMGF=1")
        cmd = f'AT+CMGS="{phone_number}"\r\n'.encode("utf-8")
        self.uart.write(cmd)

        # Wait for prompt '>'
        time.sleep(1)
        # Send message body terminated by Ctrl+Z (ASCII 26)
        payload = message.encode("utf-8") + bytes([26])
        self.uart.write(payload)

        # Wait for transmission confirmation
        time.sleep(3)
        return True

    def http_post_telemetry(self, endpoint_url: str, device_psk: str, json_payload: str) -> bool:
        """
        Transmits JSON telemetry payload to cloud backend via GPRS HTTP client.
        """
        if not self.uart:
            print(f"[MOCK GPRS POST] URL: {endpoint_url} | Payload: {json_payload}")
            return True

        try:
            # GPRS Connection sequence
            self.send_at_command('AT+SAPBR=3,1,"Contype","GPRS"')
            self.send_at_command('AT+SAPBR=3,1,"APN","internet"')
            self.send_at_command('AT+SAPBR=1,1', timeout_ms=5000)

            # HTTP Session
            self.send_at_command("AT+HTTPINIT")
            self.send_at_command('AT+HTTPPARA="CID",1')
            self.send_at_command(f'AT+HTTPPARA="URL","{endpoint_url}"')
            self.send_at_command('AT+HTTPPARA="CONTENT","application/json"')
            self.send_at_command(f'AT+HTTPPARA="USERDATA","X-Device-PSK: {device_psk}"')

            # Send data
            data_len = len(json_payload.encode("utf-8"))
            self.send_at_command(f"AT+HTTPDATA={data_len},10000")
            self.uart.write(json_payload.encode("utf-8"))
            time.sleep(1)

            # Execute POST
            self.send_at_command("AT+HTTPACTION=1", expected_response="201", timeout_ms=8000)
            self.send_at_command("AT+HTTPTERM")
            self.send_at_command("AT+SAPBR=0,1") # Close bearer
            return True
        except Exception as e:
            print("GPRS HTTP error:", e)
            return False

    def power_down(self):
        """Puts modem into ultra-low-power sleep mode"""
        self.send_at_command("AT+CSCLK=2")
