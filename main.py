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
from math import sin

# Perceptual brightness curve — RGB output is non-linear in perceived intensity,
# so dim ramps look "jumpy". Lookup table maps linear input to gamma 2.6 output.
GAMMA = bytes(int(((i / 255.0) ** 2.6) * 255 + 0.5) for i in range(256))

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("RPi-Pico MicroPython Ver:", sys.version)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

INACTIVITY_TIMER = 7
STYLE_BYTES = 2
STYLE_ADDRESS = 0
I2C_FREQ = 1_000_000
SPI_FREQ = 4_000_000
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
INIT_SLEEP_MS = 3000

led_data_pin = Pin(22)
brightness = 0.2
oled_fps = 5
oled_screen_on = False
oled_needs_check = True
oled_displayed_state = None  # ('image', style) or ('blank',)
last_button_press = 0
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
sleep_ms(INIT_SLEEP_MS)

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

# Wrap pixels_show so OLED state checks happen at a safe point — right after
# the WS2812 frame has been clocked out and latched.
_neopixel_show = led_string.pixels_show
def _pixels_show_with_oled():
    _neopixel_show()
    _process_oled()
led_string.pixels_show = _pixels_show_with_oled


def update_oled_display(oled_timer):
    # Hard IRQ context: just flag — actual SPI work runs from main loop.
    global oled_needs_check
    oled_needs_check = True


def _process_oled():
    # Called from main-loop context after each pixels_show, where it's safe
    # to do SPI without corrupting an in-flight WS2812 transmission.
    global oled_needs_check, oled_displayed_state, oled_screen_on
    if not oled_needs_check:
        return
    oled_needs_check = False
    if (time() - last_button_press) < INACTIVITY_TIMER:
        target = ('image', led_style)
        if oled_displayed_state != target:
            display_image(img_utils.get_style_img(led_style))
            oled_displayed_state = target
            oled_screen_on = True
    else:
        if oled_displayed_state != ('blank',):
            display_image()
            oled_displayed_state = ('blank',)
            oled_screen_on = False


def button_press_isr(irq):
    global last_button_press, onboard_led, oled_needs_check
    last_button_press = time()
    onboard_led.on()
    if oled_screen_on:
        go_to_next_style()
    oled_needs_check = True
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


def do_comet():
    # Single comet sweep, head appears at start the moment the previous
    # trail tip leaves the end — same per-pixel speed, no pre-roll gap.
    trail_len = 8
    pos = 0
    while True:
        led_string.clear_pixels()
        for i in range(trail_len + 1):
            p = pos - i
            if 0 <= p < NUM_LEDS:
                v = GAMMA[max(0, 255 - i * 32)]
                led_string.pixels_set(p, (v, v, v))
        led_string.pixels_show()
        pos += 1
        if pos >= NUM_LEDS + trail_len:
            pos = 0
        if not led_style == "comet":
            return
        sleep_ms(40)


def do_aurora():
    # Slow drift through greens, cyans, blues, purples — gamma-corrected so
    # the dim end of the curve is perceptually smooth instead of stepping.
    t = 0.0
    while True:
        for i in range(NUM_LEDS):
            h = int(sin(t * 0.7 + i * 0.22) * 14000 + 35000) & 0xFFFF
            color = Neopixel.colorHSV(h, 230, 200)
            led_string.pixels_set(i, (GAMMA[color[0]], GAMMA[color[1]], GAMMA[color[2]]))
        led_string.pixels_show()
        t += 0.08
        if not led_style == "aurora":
            return
        sleep_ms(50)


def do_ember():
    # Warm-tone sibling to aurora — drifts through greens, yellows, oranges.
    # Hue range ~5000..21000 (16-bit) covers red-orange through yellow to green.
    t = 0.0
    while True:
        for i in range(NUM_LEDS):
            h = int(sin(t * 0.7 + i * 0.22) * 8000 + 13000) & 0xFFFF
            color = Neopixel.colorHSV(h, 230, 200)
            led_string.pixels_set(i, (GAMMA[color[0]], GAMMA[color[1]], GAMMA[color[2]]))
        led_string.pixels_show()
        t += 0.08
        if not led_style == "ember":
            return
        sleep_ms(50)


def do_vortex():
    # Razer Vortex-inspired ambient swirl: rainbow bands rotate through
    # the tree. Brightness held flat — depth comes from a wider hue
    # spread across rows and radial distance, plus a saturation shimmer.
    t = 0.0
    while True:
        phase = int(t * 3800)
        for row_index in range(NUM_ROWS):
            row = ROWS_BTM_2_TOP[row_index]
            center = (len(row) - 1) / 2
            for slot_index in range(len(row)):
                led = row[slot_index]
                distance = abs(slot_index - center) / (center + 1)
                wave = sin(t * 1.3 + row_index * 0.7 + slot_index * 1.1)
                h = int(phase + row_index * 8200 + distance * 21000 + wave * 5200) & 0xFFFF
                s = 205 + int((wave + 1.0) * 25)
                color = Neopixel.colorHSV(h, s, 200)
                led_string.pixels_set(led - 1, (GAMMA[color[0]], GAMMA[color[1]], GAMMA[color[2]]))
        led_string.pixels_show()
        t += 0.07
        if not led_style == "vortex":
            return
        sleep_ms(22)


def do_solstice():
    # Warm amber lower, cool aqua upper, with a hue ripple that climbs
    # through the rows. Brightness held flat — depth comes from richer
    # per-pixel hue swings and a saturation shimmer riding on top.
    t = 0.0
    while True:
        breath = (sin(t * 0.55) + 1.0) / 2.0
        ripple_phase = t * 1.8
        for row_index in range(NUM_ROWS):
            row = ROWS_BTM_2_TOP[row_index]
            row_mix = row_index / (NUM_ROWS - 1)
            base_hue = int(7500 + row_mix * 34500)
            ripple = sin(ripple_phase - row_index * 0.7)
            for slot_index in range(len(row)):
                led = row[slot_index]
                shimmer = sin(t * 1.4 + row_index * 0.8 + slot_index * 1.4)
                h = int(base_hue + shimmer * 4400 + breath * 2400 + ripple * 3000) & 0xFFFF
                s = 200 + int((shimmer + 1.0) * 25)
                color = Neopixel.colorHSV(h, s, 180)
                led_string.pixels_set(led - 1, (GAMMA[color[0]], GAMMA[color[1]], GAMMA[color[2]]))
        led_string.pixels_show()
        t += 0.06
        if not led_style == "solstice":
            return
        sleep_ms(28)


def get_date_string(now):
    year = str(now[0])
    month = img_utils.get_month(now[1])
    day = now[2]
    day_of_wk = img_utils.get_day_of_week(now[3])
    return ''.join([day_of_wk, ', ', "{0}{1:2}".format(month, day), ', ', year])


def get_time_tuple(now):
    hours = now[4]
    minutes = now[5]
    return (int(hours / 10), hours % 10, int(minutes / 10), minutes % 10)


def display_date_and_time():
    current_time = rtc.datetime()
    # Clear oled display
    oled.fill(0)
    create_date_text(get_date_string(current_time))
    create_time_image(get_time_tuple(current_time))
    create_style_text(led_style)
    oled.show()


def create_style_text(style_str):
    oled.text(': '.join(['LEDs', style_str]), mini_style_start_x, mini_style_start_y)


def create_date_text(date_str):
    oled.text(date_str, date_start_x, date_start_y)


def create_time_image(digits_tuple):
    (tens_hr, ones_hr, tens_min, ones_min) = digits_tuple
    # load frame buffs for time image
    tens_hr_fb = get_frame_buffer(img_utils.get_time_img(tens_hr), digit_px_x, digit_px_y)
    ones_hr_fb = get_frame_buffer(img_utils.get_time_img(ones_hr), digit_px_x, digit_px_y)
    colon_fb = get_frame_buffer(img_utils.get_time_img(COLON), colon_px_x, digit_px_y)
    tens_min_fb = get_frame_buffer(img_utils.get_time_img(tens_min), digit_px_x, digit_px_y)
    ones_min_fb = get_frame_buffer(img_utils.get_time_img(ones_min), digit_px_x, digit_px_y)
    # add image chunks
    oled.blit(tens_hr_fb, tens_hr_digit_start_x, digit_start_y)
    oled.blit(ones_hr_fb, ones_hr_digit_start_x, digit_start_y)
    oled.blit(colon_fb, colon_start_x, digit_start_y)
    oled.blit(tens_min_fb, tens_min_digit_start_x, digit_start_y)
    oled.blit(ones_min_fb, ones_min_digit_start_x, digit_start_y)


style_func_list = [
    do_rainbow_cycle, do_chase, do_fill, do_off, do_red,
    do_yellow, do_green, do_cyan, do_blue, do_purple, do_white,
    do_firefly, do_blend, do_flash, do_chasebow, do_rainbow_ttb,
    do_rainbow_btt, do_chase_ttb, do_chase_btt,
    do_comet, do_aurora, do_ember, do_vortex, do_solstice
]

style_to_func_dict = dict(zip(led_style_list, style_func_list))
show_current_style(led_style)
last_button_press = time()
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
oled_timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
while True:
    style_to_func_dict.get(led_style, do_rainbow_cycle)()