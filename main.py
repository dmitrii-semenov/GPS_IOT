import machine
import time
import BG77

_REMOTE_SERVER_IP_ = "147.229.146.40"
_REMOTE_SERVER_PORT_ = 1883
_CLIENT_ID_ = "ac24c3a0-f904-11ee-b0f6-299dee8b9dbf"
_ACCESS_TOKEN_ = "052du7z8d2xagimrfdsh"
_PASSWORD_ = ""

_REMOTE_SERVER_IP_PROXY_ = "147.229.146.40"
_REMOTE_SERVER_PORT_PROXY_ = 7007

_SENDING_INTERVAL_ = 10*1000       #30*60*1000  30 minutes in milliseconds

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
time.sleep(3)
module.setAPN("lpwa.vodafone.iot")
time.sleep(5)
module.attachToNetwork()
time.sleep(5)

# Open socket
module.sendCommand(f"AT+QIOPEN=1,1,\"UDP\",\"{_REMOTE_SERVER_IP_PROXY_}\",{_REMOTE_SERVER_PORT_PROXY_}\r\n")
time.sleep(3)

# Check network registration status using AT+CEREG?
cereg_response = module.sendCommand("AT+CEREG?\r\n")
time.sleep(1)
print("Network Registration Status (CEREG):", cereg_response)
coordinates_num = len(coordinates)
a = 0

# Enable PSM mode
module.sendCommand(f"AT+CPSMS=1,,,\"00000100\",\"00001111\"\r\n") # TAU = 40 min, Active time = 30 sec
time.sleep(1)

while True:
# WAKE UP
    module.sendCommand(f"WKUP\r\n") # Wake up module
    time.sleep(1)
    
    # Send message
    latitude, longitude = coordinates[a]
    gps_data = f"\"latitude\":{latitude},\"longitude\":{longitude}"
    module.sendCommand(f"AT+QISEND=1,{len(gps_data)}\r\n")
    time.sleep(1)
    module.sendCommand(gps_data + "\r\n")
    a = a + 1
    if a == coordinates_num:
        a = 0
    
# Check downlink message
    time.sleep(5)
    # disregard the serial buffer content
    bg_uart.read(bg_uart.in_waiting)
    # read the downlink message
    module.sendCommand(f"AT+QIRD=1\r\n")
    time.sleep(1)
    if bg_uart.in_waiting > 0:
        message = bg_uart.read(bg_uart.in_waiting)
        message = message.decode("utf-8")
        message.split(",")
        # decide whether to change sending interval
        if message[0] == "OK":         
            if message[1] == "TRUE":
                _SENDING_INTERVAL_ = 1*60*1000 # 1 minute in milliseconds
            elif message[1] == "FALSE":
                _SENDING_INTERVAL_ = 30*60*1000
        else:
            message = "Not a expected response."
    else:
        message = "Nothing received from the server."
    print(message)

# Sleep mode activation
    machine.lightsleep(_SENDING_INTERVAL_) 
#    time.sleep(10)
