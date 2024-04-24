## Authors
- Dmitrii Semenov
- Radoslav Tomčala

# Use Case
The [GPS-tracker](https://github.com/dmitrii-semenov/GPS_IOT) is a portable device designed for use by delivery services to easily monitor package locations. In cases of emergency or theft, it can switch from a standard update period of 30 minutes to a quick 1-minute refresh rate. The last known location is displayed on the [Thingsboard](https://thingsboard.io/) portal, allowing monitoring of the delivery. The device operates on battery power to maintain portability.
# Instructions
After being connected to power, the device automatically configures itself and should begin sending coordinates to the desired server in about 20 seconds. Afterward, it enters power-saving mode until the waiting time expires and proceeds to send another message. When connected to the server, you have the ability to change the frequency of incoming data by flipping a switch on a dashboard. The device doesn't recognize this change immediately, but it must wait for another uplink to receive a confirmation message with the current switch status. If the state has changed, the device adapts to the desired mode of operation.

## Showcase
![image](https://github.com/dmitrii-semenov/GPS_IOT/assets/124372068/980d3469-7b51-4cf0-ac19-71ac5d9c86a7)
https://github.com/dmitrii-semenov/GPS_IOT/blob/main/demo.mov
## Hardware
The main controlling unit is the MCU (Microcontroller Unit), specifically [Raspberry Pico](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html), connected to a [BG77](https://www.quectel.com/wp-content/uploads/2021/03/Quectel_BG77_LPWA_Specification_V1.6.pdf) module providing NB-IoT capability. In the full version, the MCU would connect to a battery pack, and a GPS module would be added via a serial port.

![image](https://github.com/dmitrii-semenov/GPS_IOT/assets/124372068/3832dd8c-1a9f-462c-a1c4-9f814cd84af3)

## Data Transmission
The NB-IoT module sends data according to the set interval to a proxy server using UDP communication protocol. This approach bypasses the requirement of [Thingsboard](https://thingsboard.io/) to use TCP-based MQTT and minimizes packet quantity. Upon receiving an uplink, the proxy sends a confirmation message that also includes the status of a fast monitoring switch.

![image](https://github.com/dmitrii-semenov/GPS_IOT/assets/124372068/51cd049b-6daa-43c7-a06e-b2fb7b4205af)

### GPS Coordinates Format
```python
coordinates = [(longitude, latitude)]
```

### Response Examples
```python
message = "OK,True"  # Uplink was received and forwarded, quicker updates enabled
message = "OK,False"  # Uplink was received and forwarded, quicker updates disabled
```
## Theoretical battery live
![image](https://github.com/dmitrii-semenov/GPS_IOT/assets/124372068/b7cd45a4-c8a0-481e-b655-236af3c625cb)
![image](https://github.com/dmitrii-semenov/GPS_IOT/assets/124372068/ae1205d9-b47a-40e0-8ba7-127b8f5ee864)

## Used Solutions and Issues
For data transmission, NB-IoT technology was chosen due to its coverage, low hardware cost and low power consumption. Also because of the nature of this project, the main disadvatanges as high latency, low amount of data transition and possible lags do not affect us in any significant way. However, as it's a paid solution, minimizing sent and received data was essential. Hence, UDP protocol was utilized for its fire-and-forget nature. To conserve power, the PSM (Power Saving Mode) was employed, as no data is expected during sleep periods. Although a sleep mode for the MCU was considered, issues with the RP2040 prompted its continuous operation. This issue could be solved by using a different MCU, such as the ESP32.  When it comes to battery power and a GPS module, neither of these components are included in the solution due to limitations of the development board used. Although the battery issue could potentially be resolved, the larger problem lies with the GPS module. The issue is from the BG77 module utilizing the serial port of the onboard MCU, and the capability to add another device is not implemented on the board. While both of these issues are fixable, they extend beyond the scope of this project.

