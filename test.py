import machine
import time
import BG77

_REMOTE_SERVER_IP_ = "147.229.146.40"
_REMOTE_SERVER_PORT_ = 1883
_CLIENT_ID_ = "ac24c3a0-f904-11ee-b0f6-299dee8b9dbf"
_ACCESS_TOKEN_ = "052du7z8d2xagimrfdsh"
_PASSWORD_ = ""

coordinates = [
    (49.218319, 16.581795),
    (49.224934, 16.599390),
    (49.202283, 16.619560),
    (49.204638, 16.571667),
]

# Initialize UART for BG77 module
bg_uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rxbuf=256, rx=machine.Pin(1), timeout=0, timeout_char=1)
bg_uart.write(bytes("AT\r\n", "ascii"))

# Initialize BG77 module
module = BG77.BG77(bg_uart, verbose=True, radio=False)
time.sleep(3)

# Set radio mode and APN configuration
module.setRadio(1)
time.sleep(1)
module.setAPN("lpwa.vodafone.iot")
time.sleep(1)
module.attachToNetwork()
time.sleep(5)

# Open MQTT connection to ThingsBoard
module.sendCommand("AT+QCSCON=1\r\n")
time.sleep(5)
module.sendCommand(f"AT+QMTCFG=\"version\",1,4\r\n")
time.sleep(3)
module.sendCommand(f"AT+QMTOPEN=1,\"{_REMOTE_SERVER_IP_}\",{_REMOTE_SERVER_PORT_}\r\n")
time.sleep(1)

# MQTT connection to ThingsBoard
module.sendCommand(f"AT+QMTCONN=1,\"{_CLIENT_ID_}\",\"{_ACCESS_TOKEN_}\",\"{_PASSWORD_}\"\r\n")
time.sleep(1)

# Check network registration status using AT+CREG?
creg_response = module.sendCommand("AT+CREG?\r\n")
time.sleep(1)
print("Network Registration Status (CREG):", creg_response)

# Check extended network registration status using AT+CEREG?
cereg_response = module.sendCommand("AT+CEREG?\r\n")
time.sleep(1)
print("Extended Network Registration Status (CEREG):", cereg_response)

# Start send the GPS positions
while True:
    for item in coordinates:
        latitude, longitude = item
        gps_data = f"{{\"latitude\":{latitude},\"longitude\":{longitude}}}"
        module.sendCommand(f"AT+QMTPUB=1,0,0,0,\"gps_topic\",{len(gps_data)}\r\n")
        time.sleep(1)
        module.sendCommand(gps_data + "\r\n")
        time.sleep(10)  # Wait for 10 seconds before sending the next coordinate
