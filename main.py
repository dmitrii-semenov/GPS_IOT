import machine
import time
import BG77

# ThingsBoard configuration
_REMOTE_SERVER_IP_ = "147.229.146.40"
_REMOTE_SERVER_PORT_ = 1883
_CLIENT_ID_ = "ac24c3a0-f904-11ee-b0f6-299dee8b9dbf"
_ACCESS_TOKEN_ = "052du7z8d2xagimrfdsh"
_PASSWORD_ = ""

# PROXY configuration
_REMOTE_SERVER_IP_PROXY_ = "147.229.146.40"
_REMOTE_SERVER_PORT_PROXY_ = 7007

_SENDING_INTERVAL_F_ = 30*60 # in normal mode (30 minutes)
_SENDING_INTERVAL_T_ = 60 # in fast-tracking mode (1 minute)

coordinates = [
    (50.023859, 14.544091),
    (49.961500, 14.619535),
    (49.901836, 14.727313),
    (49.828195, 14.854490),
    (49.761405, 14.955801),
    (49.686155, 15.100223),
    (49.587039, 15.244645),
    (49.447096, 15.583067),
    (49.336258, 16.014177),
    (49.247689, 16.320265),
    (49.158960, 16.550909),
    (49.216722, 16.611265),
]

# Initialize UART for BG77 module
bg_uart = machine.UART(0, baudrate=115200, tx=machine.Pin(0), rxbuf=256, rx=machine.Pin(1), timeout=0, timeout_char=1)
bg_uart.write(bytes("AT\r\n", "ascii"))

# Initialize BG77 module
module = BG77.BG77(bg_uart, verbose=True, radio=False)
time.sleep(3)

# Set radio mode and APN configuration
module.setRadio(1)
time.sleep(5)
module.setAPN("lpwa.vodafone.iot")
time.sleep(1)

# Connect to the network
module.sendCommand("AT+COPS=1,2,23003\r\n")
time.sleep(5)

# Open socket
module.sendCommand(f"AT+QIOPEN=1,1,\"UDP\",\"{_REMOTE_SERVER_IP_PROXY_}\",{_REMOTE_SERVER_PORT_PROXY_}\r\n")
time.sleep(5)

# Check network registration status using AT+CEREG?
cereg_response = module.sendCommand("AT+CEREG?\r\n")
time.sleep(2)
print("Network Registration Status (CEREG):", cereg_response)

# Disable PSM (if set by default)
module.sendCommand(f"AT+CPSMS=0\r\n")
time.sleep(5)

coordinates_num = len(coordinates)
a = 0
_SENDING_INTERVAL_ = _SENDING_INTERVAL_F_

while True:
    # WAKE UP
    print("Wake up")
    module.sendCommand("WKUP\r\n")
    time.sleep(5)
    
    # Enable PSM mode
    module.sendCommand(f"AT+CPSMS=1,,,\"00000100\",\"00001000\"\r\n") # TAU = 40 min, Active time = 16 sec
    time.sleep(1)
    
    # GPS location
    #module.sendCommand(f"AT+QGPS=1\r\n")
    #time.sleep(0.5)
    #gps_data_meas = module.sendCommand(f"AT+QGPSLOC=2\r\n")
    #time.sleep(0.5)
    #print("GPS measured data:", gps_data_meas)
    #module.sendCommand(f"AT+QGPS=0\r\n")
    #time.sleep(0.5)
    
    # Send message
    latitude, longitude = coordinates[a]
    gps_data_vector = f"\"latitude\":{latitude},\"longitude\":{longitude}"
    module.sendCommand(f"AT+QISEND=1,{len(gps_data_vector)}\r\n")
    time.sleep(2)
    module.sendCommand(gps_data_vector + "\r\n")
    a = a + 1
    if a == coordinates_num:
        a = 0
    
    # Check downlink message
    message = module.sendCommand(f"AT+QIRD=1\r\n")
    time.sleep(3)
    splt_message = message.split(",")
    if len(splt_message) == 2:         
        if splt_message[1] == "True\r\n\r\nOK":
            _SENDING_INTERVAL_ = _SENDING_INTERVAL_T_
            message = "Switch set to ON position"
        elif splt_message[1] == "False\r\n\r\nOK":
            _SENDING_INTERVAL_ = _SENDING_INTERVAL_F_
            message = "Switch set to OFF position"
        else:
            message = "Not a expected response."
    else:
        message = "No Change"
    print(message)
    print("Go to sleep")
    time.sleep(1)
    
    # Wait
    time.sleep(_SENDING_INTERVAL_)