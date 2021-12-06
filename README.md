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

This project was designed for a decorative Christmas tree made out of cedar which stands about two feet in height. It consists of a Raspberry Pi Pico, a string of ws2812 neopixels, a 128x64 pixel (model: SSD1306) OLED display, an EEPROM (model: 24LC512), a standard push-button, and a esp8266 esp-01 module. The string of lights serve as the lights on the wooden Christmas tree and are controlled by one wire sending data in series to the lights. each new received value pushes the previous down the line to the next light. The different patterns of the lights are cycled through by pressing the push-button. The OLED display communication protocol is SPI and this display is used to give feedback to the user in form of the name of the LED string lighting style name. The time will be displayed after no button activity has occurred in a certain number of seconds (TBD). The time is obtained by using the esp8266 module to connect to the internet through the LAN wifi and obtain the time from a time server. Each time the led string lighting style changes, the array index of that style is stored in the EEPROM so that on next start up that setting is immediately recalled and used. I2C protocol is used to talk to the EEPROM. There is also a standalone LED that indicates whether wifi is connected or not (red/green common cathode LED).

## Prerequisites

The following classes (which are all in this repo) must be manually loaded onto the pico for this project to work:

- base64.py
- EEPROM_24LC512.py
- esp8266.py
- httpParser.py
- image_utils.py
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

- finish PCB
- make rainbow top to bottom
- make a chase from top to bottom

### Template for code

```python
from machine import Pin
from esp8266 import ESP8266
import time, sys
```
