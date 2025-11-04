# Example using PIO to drive a set of WS2812 LEDs.

import sys
from machine import Pin, SPI, Timer, I2C
from EEPROM_24LC512 import EEPROM_24LC512
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms, time
import img_utils
from neopixel import Neopixel
import random

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("RPi-Pico MicroPython Ver:", sys.version)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

INACTIVITY_TIMER = 7
STYLE_BYTES = 2
STYLE_ADDRESS = 0
I2C_FREQ = 1_000_000
SPI_FREQ = 115_200
SPI_PORT = 0
# Configure the number/order of WS2812 LEDs.
ROW0 = [18, 19, 20, 21, 22, 23, 24, 25]
ROW1 = [15, 16, 17, 26, 27, 28]
ROW2 = [12, 13, 14, 29,30, 31]
ROW3 = [10, 11, 32, 33]
ROW4 = [1, 2, 8, 9]
ROW5 = [3, 7]
ROW6 = [4, 6]
ROW7 = [5]
ROWS_BTM_2_TOP = [ROW0, ROW1, ROW2, ROW3, ROW4, ROW5, ROW6, ROW7]
ROWS_TOP_2_BTM = ROWS_BTM_2_TOP[::-1]
NUM_ROWS = len(ROWS_BTM_2_TOP)
NUM_LEDS = sum(len(x) for x in ROWS_BTM_2_TOP)

led_data_pin = Pin(22)
brightness = 0.2
oled_fps = 5
dc = Pin(17)
rst = Pin(20)
cs = Pin(16)
mosi = Pin(19)
sck = Pin(18)
fullscreen_px_x = 128  # SSD1306 horizontal resolution
fullscreen_px_y = 64   # SSD1306 vertical resolution
none_px_x = 8
none_px_y = 1
button = Pin(15, Pin.IN, Pin.PULL_UP)
onboard_led = Pin(25, Pin.OUT)
sda = Pin(12)
scl = Pin(13)
i2c = I2C(0, sda=sda, scl=scl, freq=I2C_FREQ)
i2c_devices = i2c.scan()
print("I2C Devices: {}".format(i2c_devices))
eeprom = EEPROM_24LC512(i2c, i2c_devices[0])


def get_frame_buffer(img_ba, x_px, y_px):
    if img_ba is None:
        return framebuf.FrameBuffer(img_utils.get_time_img(None), none_px_x, none_px_y, framebuf.MONO_HLSB)
    else:
        return framebuf.FrameBuffer(img_ba, x_px, y_px, framebuf.MONO_HLSB)


def display_image(byte_array=None):
    if byte_array:
        # Load image into the framebuffer64)
        fb = get_frame_buffer(byte_array, fullscreen_px_x, fullscreen_px_y)
        # Clear oled display
        oled.fill(0)
        oled.blit(fb, 1, 1)
        oled.show()
    else:
        oled.fill(0)
        oled.show()


def write_style_index_to_eeprom(index):
    eeprom.write(STYLE_ADDRESS, index.to_bytes(STYLE_BYTES, 'big'))
    print("Style index wrote to EEPROM: {}".format(index))


# Create an SPI Object and use it for oled display
oled_timer = Timer()
spi = SPI(SPI_PORT, SPI_FREQ, mosi=mosi, sck=sck)
oled = SSD1306_SPI(fullscreen_px_x, fullscreen_px_y, spi, dc, rst, cs)
display_image(img_utils.get_system_ba("hello"))

# initialize LED string stuff
led_style_list = img_utils.get_style_list()
style_index = int.from_bytes(eeprom.read(STYLE_ADDRESS, STYLE_BYTES), 'big')
if style_index >= len(led_style_list):
    style_index = 0
    write_style_index_to_eeprom(style_index)
print("Style index from EEPROM: {}".format(style_index))
led_style = led_style_list[style_index]
led_string = Neopixel(led_data_pin, NUM_LEDS, brightness)
led_string.clear_pixels()
led_string.pixels_show()


def update_oled_display(oled_timer):
    if (time() - last_button_press) < INACTIVITY_TIMER:
        display_image(img_utils.get_style_img(led_style))
    else:
        display_image()  # display blank screen


def button_press_isr(irq):
    global last_button_press, onboard_led
    last_button_press = time()
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


def do_rainbow_cycle(wait=20):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = int(i * 255 / NUM_LEDS) + j
            led_string.pixels_set(i, Neopixel.wheel(rc_index & 255))
        led_string.pixels_show()
        if not led_style == "rainbow":
            break
        sleep_ms(wait)


def color_chase(color, wait):
    for i in range(NUM_LEDS):
        led_string.pixels_set(i, color)
        sleep_ms(wait)
        led_string.pixels_show()
        if not led_style == "chase":
            break
    sleep_ms(20)


def vertical_color_chase(color, wait, dir, rows):
    chase_direction = ''.join([dir, "-cha"])
    for i in range(NUM_ROWS):
        [led_string.pixels_set(led-1, color) for led in rows[i]]
        sleep_ms(wait)
        led_string.pixels_show()
        if not led_style == chase_direction:
            return
    sleep_ms(20)


def do_rainbow_ttb(wait=10):
    # rows need to be traversed in opposite dir of rainbow
    vertical_rainbow(wait, "ttb", ROWS_BTM_2_TOP)


def do_rainbow_btt(wait=10):
    # rows need to be traversed in opposite dir of rainbow
    vertical_rainbow(wait, "btt", ROWS_TOP_2_BTM)


def vertical_rainbow(wait, dir, rows):
    bow_direction = ''.join([dir, "-bow"])
    for j in range(255):
        for i in range(NUM_ROWS):
            rc_index = int(i * 255 / NUM_ROWS) + j
            [led_string.pixels_set(led-1, Neopixel.wheel(rc_index & 255)) for led in rows[i]]
        led_string.pixels_show()
        if not led_style == bow_direction:
            break
        sleep_ms(wait)


def do_chase():
    for color in led_string.get_colors():
        color_chase(color, 10)
        if not led_style == "chase":
            return


def do_chase_ttb():
    vertical_chase("ttb", ROWS_TOP_2_BTM)


def do_chase_btt():
    vertical_chase("btt", ROWS_BTM_2_TOP)


def vertical_chase(dir, rows, wait=45):
    chase_direction = ''.join([dir, "-cha"])
    for color in led_string.get_colors():
        vertical_color_chase(color, wait, dir, rows)
        if not led_style == chase_direction:
            return


def do_chasebow():
    for j in range(255):
        mask = j % 2
        for i in range(NUM_LEDS):
            rc_index = int(i * 255 / NUM_LEDS) + j*16
            color = Neopixel.wheel(rc_index & 255)
            led_string.pixels_set(i, (color[0]*mask, color[1]*mask, color[2]*mask))
            sleep_ms(20)
            led_string.pixels_show()
            if not led_style == "chasebow":
                return
        sleep_ms(10)


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
    colors = led_string.get_firefly_colors()
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
        sleep_ms(20)
        hue += 150
        if not led_style == "blend":
            return


def do_flash():
    led_string.pixels_fill((10, 10, 10))
    led_string.pixels_show()
    while True:
        for i in range(NUM_LEDS):
            for j in range(NUM_LEDS):
                led_string.pixels_set(j,\
                    (abs(i+j) % 10, abs(i-(j+3)) % 10, abs(i-(j+6)) % 10))
            led_string.pixels_show()
            sleep_ms(50)
            if not led_style == "flash":
                return


style_func_list = [
    do_rainbow_cycle, 
    do_chase, 
    do_fill, 
    do_off, 
    do_red, 
    do_yellow, 
    do_green, 
    do_cyan, 
    do_blue, 
    do_purple, 
    do_white,
    do_firefly, 
    do_blend, 
    do_flash, 
    do_chasebow, 
    do_rainbow_ttb,
    do_rainbow_btt, 
    do_chase_ttb, 
    do_chase_btt
]

style_to_func_dict = dict(zip(led_style_list, style_func_list))
show_current_style(led_style)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
oled_timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
last_button_press = time()
while True:
    style_to_func_dict.get(led_style, do_rainbow_cycle)()