# Raspberry Pi Pico with ws2812 LED string, SSD1306 OLED display, esp8266 (esp-01), and 24LC512 EEPROM. "Christmas Lights"

[![GitHub version](https://img.shields.io/github/release/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-release)
[![GitHub download](https://img.shields.io/github/downloads/jcksnvllxr80/raspi_pico_christmas_tree/total.svg)](lib-release)
[![GitHub stars](https://img.shields.io/github/stars/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-stars)
[![GitHub issues](https://img.shields.io/github/issues/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](lib-licence)

## Image of project // still a WIP

<p align="center">
<img src="https://live.staticflickr.com/65535/51725697269_1f4f05c453_k.jpg" width="800">
</p>

<p align="center">
<img src="https://live.staticflickr.com/65535/51717997987_277b59fbd0_k.jpg" width="800">
</p>

## Description

This project was designed for a decorative Christmas tree made out of cedar which stands about two feet in height. It consists of a Raspberry Pi Pico, a string of ws2812 neopixels, a 128x64 pixel (model: SSD1306) OLED display, an EEPROM (model: 24LC512), and a standard push-button. The string of lights serve as the lights on the wooden Christmas tree and are controlled by one wire sending data in series to the lights. each new received value pushes the previous down the line to the next light. The different patterns of the lights are cycled through by pressing the push-button. The OLED display communication protocol is SPI and this display is used to give feedback to the user in form of the name of the LED string lighting style name. A blank screen will be displayed after no button activity has occurred in a certain number of seconds (TBD). Each time the led string lighting style changes, the array index of that style is stored in the EEPROM so that on next start up that setting is immediately recalled and used. I2C protocol is used to talk to the EEPROM.  

## Prerequisites

The following classes (which are all in this repo) must be manually loaded onto the pico for this project to work:

- EEPROM_24LC512.py
- img_utils.py
- neopixel.py
- ssd1306.py
- main.py

## Text Image Creation

  1. open paint and set the properties canvas size to the number of pixels on the display (128,64)
  2. add some text with cool font and different size as well as bold and get it centered in the canvas
  3. select all (ctrl+a) then right click the image and invert colors
  4. save the image to a place easy to get to
  5. got to <https://javl.github.io/image2cpp/> and open the image from the previous step
  6. convert it and then use the *_img files in this proj as a template on how to use that data

## TODO

- use various waveforms to mask the brightness of the strip... i.e. cos, tan, sawtooth, triangle
- similarly to above, mask the waveforms along the time domain

### USE THONNY TO WRITE THE FOLLOWING CODE TO PI PICO WHICH IS CONTROLLING ESP8266-01

```python
from machine import UART, Pin
user_agent="RPi-Pico"
host="worldtimeapi.org"
path="/api/timezone/America/New_York"
getHeader = "GET "+path+" HTTP/1.1\r\n"+"Host: " + host+"\r\n"+"User-Agent: "+user_agent+"\r\n"+"\r\n"
txData = "AT+CIPSEND="+str(len(getHeader))+"\r\n"
UART_Tx_BUFFER_LENGTH = 1024
UART_Rx_BUFFER_LENGTH = 1024*2
UART_BAUD = 115_200
uart_port = 1
uart_tx_pin = 4
uart_rx_pin = 5
esp = UART(uart_port, baudrate=UART_BAUD, tx=Pin(uart_tx_pin), rx=Pin(uart_rx_pin), txbuf=UART_Tx_BUFFER_LENGTH, rxbuf=UART_Rx_BUFFER_LENGTH)
esp.write('AT\r\n'); esp.read()
esp.write('AT+GMR\r\n'); esp.read()
esp.write('ATE1\r\n'); esp.read()
esp.write('AT+GMR\r\n'); esp.read()
esp.write('AT+CWMODE_CUR=3\r\n'); esp.read()
esp.write('AT+CWJAP_CUR="<YOUR_SSID>","<YOUR_PASSWORD>"\r\n'); esp.read()
esp.write('AT+CIPSTATUS\r\n'); esp.read()
esp.write('AT+CIPSTART="TCP","worldtimeapi.org",80\r\n'); esp.read()
esp.write('AT+CWLIF\r\n'); esp.read()
esp.write('AT+HTTPCLIENT=1,0,"http://httpbin.org/get","httpbin.org","/get",1\r\n'); esp.read()
esp.write('AT+CIPSTART="TCP","worldtimeapi.org",80\r\n'); esp.read()
esp.write("AT+CIPSEND="+str(len(getHeader))+"\r\n"); esp.read()
esp.write(getHeader); esp.read()
esp.write("AT+PING=\"google.com\"\r\n"); esp.read()
esp.write("AT+PING=\"8.8.8.8\"\r\n"); esp.read()
esp.write("AT+CWJAP?\r\n"); esp.read(); esp.read()
esp.write("AT+CWQAP\r\n"); esp.read(); esp.read()
```
