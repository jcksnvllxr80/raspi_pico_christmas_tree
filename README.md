# Raspberry Pi Pico with ws2812 LED string, SSD1306 OLED display, and 24LC512 EEPROM. "Christmas Lights"

[![GitHub version](https://img.shields.io/github/release/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-release)
[![GitHub download](https://img.shields.io/github/downloads/jcksnvllxr80/raspi_pico_christmas_tree/total.svg)](lib-release)
[![GitHub stars](https://img.shields.io/github/stars/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-stars)
[![GitHub issues](https://img.shields.io/github/issues/jcksnvllxr80/raspi_pico_christmas_tree.svg)](lib-issues)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](lib-licence)

## Image of project in its current phase (WIP)

<p align="center">
<img src="https://flic.kr/p/2mNhh1A" width="800">
</p>

## Drive a set of WS2812 LEDs

- Use a micropython IDE to upload the script file, examples/led_strip/main.py, to the pico and connect 3 pins to the light strip
  - data --> GPIO22
  - vcc  --> vcc
  - gnd  --> gnd

## Text Image Creation

  1. open paint and set the properties canvas size to the number of pixels on the display (128,64)
  2. add some text with cool font and different size as well as bold and get it centered in the canvas
  3. select all (ctrl+a) then right click the image and invert colors
  4. save the image to a place easy to get to
  5. got to <https://javl.github.io/image2cpp/> and open the image from the previous step
  6. convert it and then use the *_img files in this proj as a template on how to use that data

## TODO

- get wifi working with the ESP8266
