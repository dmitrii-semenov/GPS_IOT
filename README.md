# GPS_IOT## Authors: Dmitrii Semenenov, Radoslav Tomčala

# Use case
This GPS-tracker is a portable device that is supposed to be used by delivery services for easy package location monitoring and in case of emergency or theft, is able to switch from a standart update period of 30 minutes to a quick 1 minute refresh rate. Last known location is displayed on portal Thingsboard where you can monitor the delivery. Everything is battery powered to preserve portability.

## Instructions
After connecting to power, the device automaticly configures itself and should begin sending coordinates to desired server in about 20 seconds. After that it goes into power saving mode until the waiting time expires and proceeds to send another message. When you connect to the server you have a ability to change the frequency of incoming data by flipping a switch on a dashboard. The device doesnt recognize this chagne immideatly but it must wait for another uplink in order to a confirmation message with a current switch status. If the state changed, the device adapts the desired mode of operation.




## Hardware
As a main controlling unit we use MCU unit. In this case Raspberry pico, that is connected to a BG77 module which provides NB-IoT capability. In the full version, the MCU would be connected to a battery pack and a GPS module would be added via serial port.

![[IoT.drawio 1.png]]
## Data transmission
NB-IoT module sends the data according to the set up interval to a proxy server using a UDP communication protocol. This is done to overcome the requirment of Thingsboard to use TCP based MQTT and keep the amout of packets to minimum. After proxy recives an UPlNK, it sends a confirmation message that also includes the state of a fast monitoring switch.
![[IoT1.drawio.png]]
**GPS coordinates format**
``` python
coordinates = [(longitude,lattitude)]
```
**Message example** 
``` python
message = "OK,True" # Uplink was recived and fowarded , Quicker updates enabled
message = "OK,False" # Uplink was recived and fowarded , Quicker updates disabled
```
**Used solutions**
For data transition we decided to use NB-IoT technology because it provides us with a option of more stable connection than other technologies. But because it is a paid solutions we had to keep the amount of send and recived data to minimum. That is why we had to use UDP protocol that works in a fire and forget way. 