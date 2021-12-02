# https://techatronic.com/ssd1306-raspberry-pi-pico/

from machine import Pin, SPI
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms

spi = SPI(0, 100000, mosi=Pin(19), sck=Pin(18))
oled = SSD1306_SPI(128, 64, spi, Pin(17), Pin(20), Pin(16))
#oled = SSD1306_SPI(WIDTH, HEIGHT, spi, dc,rst, cs) use GPIO PIN NUMBERS
while True:
    try:
        for i in range(40):
            for j in range(56):

                oled.fill(0)
                oled.show()
                oled.text("HELLO WORLD", i, j)
                oled.show()
                sleep_ms(10)
    except KeyboardInterrupt:
        break