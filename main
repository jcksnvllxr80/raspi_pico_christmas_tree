# Example using PIO to drive a set of WS2812 LEDs.

import array
import rp2
from machine import Pin, SPI, Timer
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms, sleep_us, sleep
import rainbow_img, chase_img, fill_img

# Configure the number of WS2812 LEDs.
NUM_LEDS = 50
PIN_NUM = 22
brightness = 0.5
oled_fps = 5
button = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)
led_style = "rainbow"  # TODO: read from non-volatile memory
led_style_list = ["rainbow", "chase", "fill"]
pix_res_x = 128  # SSD1306 horizontal resolution
pix_res_y = 64   # SSD1306 vertical resolution
text_position = 1
timer = Timer()
spi = SPI(0, 100000, mosi=Pin(19), sck=Pin(18))
oled = SSD1306_SPI(pix_res_x, pix_res_y, spi, Pin(17), Pin(20), Pin(16))
#oled = SSD1306_SPI(WIDTH, HEIGHT, spi, dc,rst, cs) use GPIO PIN NUMBERS
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

byte_array_dict = {
    "rainbow": rainbow_img.get_img(),
    "chase": chase_img.get_img(),
    "fill": fill_img.get_img()
}

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


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        if not led_style == "rainbow":
            break
        sleep_ms(wait)


def update_oled_display(timer):
    global text_position
    try:
        # print("text position is {}".format(text_position))
        # oled.fill(0)
        # oled.show()
        # oled.text(led_style, text_position, 10)
        # oled.show()
        # sleep_ms(10)
        # if text_position >= 40:
        #     text_position = 1
        # else:
        #     text_position += 1
        display_image(byte_array_dict[led_style])
    except KeyboardInterrupt:
        pass


def button_press_isr(irq):
    global led
    led.on()
    go_to_next_style()
    led.off()


def go_to_next_style():
    global led_style
    next_index = led_style_list.index(led_style) + 1
    if len(led_style_list) <= next_index:
        next_index = 0
    led_style = led_style_list[next_index]
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


show_current_style(led_style)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
while True:
    if led_style == "rainbow":
        rainbow_cycle(0)
    elif led_style == "chase":
        do_chase()
    elif led_style == "fill":
        do_fill()