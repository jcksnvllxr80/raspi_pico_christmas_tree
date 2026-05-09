# Raspberry Pi Pico with ws2812 LED string, SSD1306 OLED display, and 24LC512 EEPROM. "Pineapple Lights"

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

This project was designed for a decorative pineapple sculpture fitted with ws2812 neopixels. It consists of a Raspberry Pi Pico, a string of ws2812 neopixels arranged in rows across the pineapple, a 128x64 pixel (model: SSD1306) OLED display, an EEPROM (model: 24LC512), and a standard push-button. The LEDs are controlled by one wire sending data in series — each new received value pushes the previous down the line to the next light. The different lighting effects are cycled through by pressing the push-button. The OLED display (SPI) shows the name of the currently active effect and goes blank after a configurable number of seconds of inactivity. Each time the effect changes, the array index of that effect is stored in the EEPROM so that on next startup that setting is immediately recalled and used. I2C protocol is used to talk to the EEPROM.

## Prerequisites

The following classes (which are all in this repo) must be manually loaded onto the pico for this project to work:

- EEPROM_24LC512.py
- img_utils.py
- neopixel.py
- ssd1306.py
- main.py

## Installing / Updating

The `tools/` directory contains one-shot installer scripts for Windows (`install.bat`) and macOS (`install.sh`) that handle everything from a completely bare machine — no git, Python, or anything else required. They install all dependencies, clone the repo, flash the correct set of files to the Pico via `mpremote`, and uninstall everything they added when done.

```
# Windows
tools\install.bat              # LEDs only (no wifi/clock)
tools\install.bat --wifi       # full firmware with wifi + NTP clock
tools\install.bat --pineapple  # pineapple LED layout

# macOS
tools/install.sh               # LEDs only (no wifi/clock)
tools/install.sh --wifi        # full firmware with wifi + NTP clock
tools/install.sh --pineapple   # pineapple LED layout
```

See [`tools/README.md`](tools/README.md) for full details on what each flag does, which files get uploaded, and how the wifi credential flow works.

## Flashing MicroPython firmware (brand new Pico)

Skip this section if the Pico already responds as a serial/COM port — it already has MicroPython.

1. Download the latest MicroPython `.uf2` for the RP2040 from **https://micropython.org/download/RPI_PICO/**
2. Hold the **BOOTSEL** button on the Pico, plug it into USB, then release the button.
3. It mounts as a drive called **RPI-RP2** — drag and drop the `.uf2` file onto that drive.
4. The Pico reboots automatically and is now running MicroPython. It will show up as a serial/COM port instead of a drive.

Once you see the COM port you're ready to use `mpremote` or run the installer scripts in `tools/`.

## Upload a single file to the Pico

The Pico must already be running MicroPython (shows up as a COM port, not as the BOOTSEL drive).

```sh
pip install --user mpremote
python -m mpremote cp main.py :main.py + reset
```

Swap `main.py` for whichever file you want to overwrite. The `+ reset` soft-resets the controller immediately after the copy so the new code takes effect. `python -m mpremote ls` lists what's on the device.

To delete a file:

```sh
python -m mpremote rm :neopixel.py
```

To dump the contents of a file to the terminal:

```sh
python -m mpremote exec "print(open('main.py').read())"
```

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

