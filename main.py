# Example using PIO to drive a set of WS2812 LEDs.

import array
import rp2
from machine import Pin, SPI, Timer, I2C
from EEPROM_24LC512 import EEPROM_24LC512
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms, sleep_us, sleep
import img_utils

STYLE_BYTES = 2
STYLE_ADDRESS = 0
# Configure the number of WS2812 LEDs.
NUM_LEDS = 33
PIN_NUM = 22
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
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))
# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    sleep_ms(10)


def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]


def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)


def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
        sleep_ms(wait)
        pixels_show()
        if not led_style == "chase":
            break
    sleep_ms(20)


def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def rainbow_cycle(wait=0):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        if not led_style == "rainbow":
            break
        sleep_ms(wait)


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


def do_fill():
    for color in COLORS:
        pixels_fill(color)
        pixels_show()
        for t in range(10):
            if not led_style == "fill":
                return
            sleep_ms(100)


def do_chase():
    for color in COLORS:
        color_chase(color, 10)
        if not led_style == "chase":
            return


def display_image(byte_array):
    # Load image into the framebuffer64)
    fb = framebuf.FrameBuffer(byte_array, pix_res_x, pix_res_y, framebuf.MONO_HLSB)
    # Clear oled display
    oled.fill(0)
    oled.blit(fb, 1, 1)
    oled.show()


style_func_list = [rainbow_cycle, do_chase, do_fill]
style_to_func_dict = dict(zip(led_style_list, style_func_list))
show_current_style(led_style)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
while True:
    style_to_func_dict.get(led_style, rainbow_cycle)()