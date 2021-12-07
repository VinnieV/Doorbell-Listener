# Doorbell Service
Listens for doorbell signals on 433MHz to detect if someone rang the doorbell.
The service will create an FCM alert, optional SMS alert (AWS SNS) and sends an api call towards a small display I have if it detected a doorbell signal.


## Prerequisites
A couple of things you will need:
* Raspberry Pi
* RF Receiver
* Antenna
* (Optional) RTL SDR

My doorbell operated on the common 433MHz frequency where a few receivers are available to capture these signals:
For example:
[433MHz Receiver (Amazon)](https://www.amazon.com/RioRand-Superheterodyne-transmitter-receiver-3400/dp/B00HEDRHG6)

For good reception and consitent results I bought a small 433 MHz antenna.
[433MHz Antenna (Amazon)](https://www.amazon.com/Electrodepot-Inches-Antenna-Magnetic-Connector/dp/B07NPX7W28/)
There are other options available, such as small 17cm coils.
Feel free to check with a vector network analyzer if the antenna you received is actually good for receiving 433MHz.
[Nano VNA](https://nanovna.com/)

[RTL SDR](https://www.rtl-sdr.com/) is optional, but I used it to capture the signal using [rtl_433](https://github.com/merbanan/rtl_433) tool by running `rtl_433 -A`.

Packages:
`sudo apt-get install python3-rpi.gpio`
`pip3 install -r requirements`

## Install

Attach 433MHz receiver to 5v, ground and I used GPIO 17 for the data line.
Solder the Antenna to the 433MHz receiver.

1. Clone repo on raspberry pi
2. Modify script to add your doorbell signal bytes (captures with RTL SDR)
3. Modify `User` & `ExecStart` variables in doorbell.service
4. Copy service file to systemd
`sudo cp doorbell.service /etc/systemd/system/`
5. Start the service
`sudo systemctl start doorbell`
6. Add the service to start at boot
`sudo systemctl enable doorbell`


## Feedback
If you notice that I am doing something stupid somewhere, you are probably right.
I am always open to constructive feedback and learn/improve.


