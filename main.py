# Example using PIO to drive a set of WS2812 LEDs.

import array
import rp2
from machine import Pin, SPI, Timer, I2C
from EEPROM_24LC512 import EEPROM_24LC512
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms
import img_utils
from neopixel import Neopixel
import random

STYLE_BYTES = 2
STYLE_ADDRESS = 0
# Configure the number of WS2812 LEDs.
NUM_LEDS = 33
led_data_pin = Pin(22)
brightness = 0.5
oled_fps = 5
dc = Pin(17)
rst = Pin(20)
cs = Pin(16)
mosi = Pin(19)
sck = Pin(18)
pix_res_x = 128  # SSD1306 horizontal resolution
pix_res_y = 64   # SSD1306 vertical resolution

button = Pin(15, Pin.IN, Pin.PULL_UP)
onboard_led = Pin(25, Pin.OUT)

sda = Pin(12)
scl = Pin(13)
i2c = I2C(0, sda=sda, scl=scl, freq=1000000)
i2c_devices = i2c.scan()
print("I2C Devices: {}".format(i2c_devices))
eeprom = EEPROM_24LC512(i2c, i2c_devices[0])


def write_style_index_to_eeprom(index):
    eeprom.write(STYLE_ADDRESS, index.to_bytes(STYLE_BYTES, 'big'))
    print("Style index wrote to EEPROM: {}".format(index))


led_style_list = img_utils.get_style_list()
style_index = int.from_bytes(eeprom.read(STYLE_ADDRESS, STYLE_BYTES), 'big')
if style_index >= len(led_style_list):
    style_index = 0
    write_style_index_to_eeprom(style_index)
print("Style index from EEPROM: {}".format(style_index))
led_style = led_style_list[style_index]

timer = Timer()

spi = SPI(0, 100000, mosi=mosi, sck=sck)
oled = SSD1306_SPI(pix_res_x, pix_res_y, spi, dc, rst, cs)
led_string = Neopixel(led_data_pin, NUM_LEDS, brightness)


def color_chase(color, wait):
    for i in range(NUM_LEDS):
        led_string.pixels_set(i, color)
        sleep_ms(wait)
        led_string.pixels_show()
        if not led_style == "chase":
            break
    sleep_ms(20)


def update_oled_display(timer):
    try:
        # print("displaying image for {}".format(led_style))
        display_image(img_utils.get_img(led_style))
    except KeyboardInterrupt:
        pass


def button_press_isr(irq):
    global onboard_led
    onboard_led.on()
    go_to_next_style()
    onboard_led.off()


def go_to_next_style():
    global led_style
    next_index = led_style_list.index(led_style) + 1
    if len(led_style_list) <= next_index:
        next_index = 0
    led_style = led_style_list[next_index]
    write_style_index_to_eeprom(next_index)
    show_current_style(led_style)


def show_current_style(style):
    print("item {}: {}".format(led_style_list.index(style)+1, style))


def do_rainbow_cycle(wait=0):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            led_string.pixels_set(i, Neopixel.wheel(rc_index & 255))
        led_string.pixels_show()
        if not led_style == "rainbow":
            break
        sleep_ms(wait)


def do_chase():
    for color in led_string.COLORS:
        color_chase(color, 10)
        if not led_style == "chase":
            return


def solid_color(color, style_compare_str):
    led_string.pixels_fill(color)
    led_string.pixels_show()
    for t in range(10):
        if not led_style == style_compare_str:
            return 1
        sleep_ms(100)


def do_fill():
    for color in led_string.COLORS:
        returned_val = solid_color(color, "fill")
        if returned_val == 1:
            return


def do_off():
    solid_color(led_string.BLACK, "off")


def do_red():
    solid_color(led_string.RED, "red")


def do_yellow():
    solid_color(led_string.YELLOW, "yellow")


def do_green():
    solid_color(led_string.GREEN, "green")


def do_cyan():
    solid_color(led_string.CYAN, "cyan")


def do_blue():
    solid_color(led_string.BLUE, "blue")


def do_purple():
    solid_color(led_string.PURPLE, "purple")


def do_white():
    solid_color(led_string.WHITE, "white")


def do_firefly():
    colors = led_string.FIREFLY_COLORS
    max_len = 20
    min_len = 5
    #pixelnum, posn in flash, flash_len, direction
    flashing = []
    num_flashes = 10
    for i in range(num_flashes):
        pix = random.randint(0, NUM_LEDS - 1)
        col = random.randint(1, len(colors) - 1)
        flash_len = random.randint(min_len, max_len)
        flashing.append([pix, colors[col], flash_len, 0, 1])

    led_string.clear_pixels()
    while True:
        led_string.pixels_show()
        for i in range(num_flashes):
            pix = flashing[i][0]
            brightness = (flashing[i][3]/flashing[i][2])
            color = (int(flashing[i][1][0]*brightness),
                    int(flashing[i][1][1]*brightness),
                    int(flashing[i][1][2]*brightness))
            led_string.pixels_set(pix, color)
            if flashing[i][2] == flashing[i][3]:
                flashing[i][4] = -1
            if flashing[i][3] == 0 and flashing[i][4] == -1:
                pix = random.randint(0, NUM_LEDS - 1)
                col = random.randint(0, len(colors) - 1)
                flash_len = random.randint(min_len, max_len)
                flashing[i] = [pix, colors[col], flash_len, 0, 1]
            flashing[i][3] = flashing[i][3] + flashing[i][4]
            if not led_style == "firefly":
                return
            sleep_ms(5)


def do_blend():
    hue = 0
    while(True):
        color = Neopixel.colorHSV(hue, 255, 150)
        led_string.pixels_fill(color)
        led_string.pixels_show()
        hue += 150
        if not led_style == "blend":
            return


def do_flash():
    led_string.pixels_fill((10, 10, 10))
    led_string.pixels_show()
    while True:
        for i in range(NUM_LEDS):
            for j in range(NUM_LEDS):
                led_string.pixels_set(j, (abs(i+j) % 10, abs(i-(j+3)) % 10, abs(i-(j+6)) % 10))
            led_string.pixels_show()
            sleep_ms(50)
            if not led_style == "flash":
                return


def display_image(byte_array):
    # Load image into the framebuffer64)
    fb = framebuf.FrameBuffer(byte_array, pix_res_x, pix_res_y, framebuf.MONO_HLSB)
    # Clear oled display
    oled.fill(0)
    oled.blit(fb, 1, 1)
    oled.show()


style_func_list = [
    do_rainbow_cycle, do_chase, do_fill, do_off, do_red, 
    do_yellow, do_green, do_cyan, do_blue, do_purple, do_white,
    do_firefly, do_blend, do_flash
]
style_to_func_dict = dict(zip(led_style_list, style_func_list))
show_current_style(led_style)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
while True:
    style_to_func_dict.get(led_style, do_rainbow_cycle)()