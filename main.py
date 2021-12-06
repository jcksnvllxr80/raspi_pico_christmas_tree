# Example using PIO to drive a set of WS2812 LEDs.

import sys
from esp8266 import ESP8266, ESP8266_WIFI_CONNECTED
from machine import Pin, SPI, Timer, I2C, RTC
from EEPROM_24LC512 import EEPROM_24LC512
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms, time
import img_utils
from neopixel import Neopixel
import random
import base64
import ujson
import re

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("RPi-Pico MicroPython Ver:", sys.version)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

CONFIG_FILE = "conf/config.json"
INACTIVITY_TIMER = 7
STYLE_BYTES = 2
STYLE_ADDRESS = 0
I2C_FREQ = 1_000_000
SPI_FREQ = 115_200
SPI_PORT = 0
UART_BAUD = 115200
uart_port = 1
uart_tx_pin = 4
uart_rx_pin = 5
# Configure the number of WS2812 LEDs.
NUM_LEDS = 33
led_data_pin = Pin(22)
# configure wifi led pins for wifi user feedback
grn_wifi_led = Pin(10, Pin.OUT)
red_wifi_led = Pin(11, Pin.OUT)
brightness = 0.5
oled_fps = 5
wifi_check_per =3_600_000
dc = Pin(17)
rst = Pin(20)
cs = Pin(16)
mosi = Pin(19)
sck = Pin(18)
fullscreen_px_x = 128  # SSD1306 horizontal resolution
fullscreen_px_y = 64   # SSD1306 vertical resolution
digit_px_x = 24
digit_px_y = 32
colon_px_x = 16
date_start_x = 0
date_start_y = 0
digit_start_y = 16
tens_hr_digit_start_x = 4
ones_hr_digit_start_x = 32
colon_start_x = 56
tens_min_digit_start_x = 72
ones_min_digit_start_x = 100
mini_style_start_x = 0 
mini_style_start_y = 56

button = Pin(15, Pin.IN, Pin.PULL_UP)
onboard_led = Pin(25, Pin.OUT)

rtc = RTC()
sda = Pin(12)
scl = Pin(13)
i2c = I2C(0, sda=sda, scl=scl, freq=I2C_FREQ)
i2c_devices = i2c.scan()
print("I2C Devices: {}".format(i2c_devices))
eeprom = EEPROM_24LC512(i2c, i2c_devices[0])


def read_config_file(filename):
    json_data = None
    with open(filename) as fp:
        json_data = ujson.load(fp)
    return json_data


def wifi_led_red():
    grn_wifi_led.off()
    red_wifi_led.on()


def wifi_led_green():
    red_wifi_led.off()
    grn_wifi_led.on()


connection = ""
wifi_led_red()


def init_esp8266():
    esp8266_at_ver = None
    print("StartUP", esp01.startUP())
    print("Echo-Off", esp01.echoING())
    print("\n")

    '''
    Print ESP8266 AT comand version and SDK details
    '''
    esp8266_at_ver = esp01.getVersion()
    if(esp8266_at_ver != None):
        print(esp8266_at_ver)

    '''
    set the current WiFi in SoftAP+STA
    '''
    esp01.setCurrentWiFiMode()
    # apList = esp01.getAvailableAPs()
    # for items in apList:
    #    print(items)


def connect_wifi():
    print("Attempting to connect to wifi AP!")
    ssid = bytes(config["wifi"]["ssid"], 'utf-8')
    password = bytes(config["wifi"]["password"], 'utf-8')
    connection_status = esp01.connectWiFi(
        base64.b64decode(ssid).decode("utf-8"),
        base64.b64decode(password).decode("utf-8")
    )
    if connection_status in ESP8266_WIFI_CONNECTED:
        print("Successfully connected to the wifi AP!")
    return connection_status


def get_wifi_conn_status(conn_status):
    if conn_status and conn_status in ESP8266_WIFI_CONNECTED:
        wifi_led_green()
        query_time_api(config["time_api"]["host"], config["time_api"]["path"])
        # print("wifi connected --> {}".format(conn_status))
    else:
        wifi_led_red()
        print("sorry, cant connect to wifi AP! connection --> {}".format(conn_status))
    return conn_status


def set_rtc(re_match, response_json):
    date_formatted_str = re_match.group(0).replace("T", "-")\
        .replace(":", "-").replace(".", "-").split("-")
    time_list = list(map(int, date_formatted_str))
    rtc.datetime((
        time_list[0],
        time_list[1],
        time_list[2],
        int(response_json['day_of_week']),
        time_list[3],
        time_list[4],
        time_list[5],
        time_list[6]
    ))


def query_time_api(host, path):
    httpCode, httpRes = esp01.doHttpGet(host, path)
    if httpRes:
        print("\nResponse from {} --> {}\n".format(host + path, httpRes))
        json_resp_obj = ujson.loads(str(httpRes))
        print("json obj --> {}\n".format(json_resp_obj))
        datetime_regex_string = r'(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d)'
        match = re.search(datetime_regex_string, json_resp_obj['datetime'])
        if match:
            set_rtc(match, json_resp_obj)
            print("RTC was set from internet time API: {}".format(match.group(0)))
        else:
            print("Error parsing time from http response; cant set RTC.")
    else:
        print("Error; no response from host: {}; cant set RTC."\
              .format(host+path))


def write_style_index_to_eeprom(index):
    eeprom.write(STYLE_ADDRESS, index.to_bytes(STYLE_BYTES, 'big'))
    print("Style index wrote to EEPROM: {}".format(index))


# create dict from config file
config = read_config_file(CONFIG_FILE)
# Create an SPI Object and use it for oled display
oled_timer = Timer()
wifi_timer = Timer()
# spi = SPI(0, 100000, mosi=mosi, sck=sck)
spi = SPI(SPI_PORT, SPI_FREQ, mosi=mosi, sck=sck)
oled = SSD1306_SPI(fullscreen_px_x, fullscreen_px_y, spi, dc, rst, cs)
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
# Create an ESP8266 Object, init, and connect to wifi AP
esp01 = ESP8266(uart_port, UART_BAUD, uart_tx_pin, uart_rx_pin)
init_esp8266()
connection = get_wifi_conn_status(connect_wifi())


def color_chase(color, wait):
    for i in range(NUM_LEDS):
        led_string.pixels_set(i, color)
        sleep_ms(wait)
        led_string.pixels_show()
        if not led_style == "chase":
            break
    sleep_ms(20)


def update_oled_display(oled_timer):
    if (time() - last_button_press) < INACTIVITY_TIMER:
        display_image(img_utils.get_img(led_style))
    else:
        display_date_and_time()


def update_conn_status(wifi_timer):
    global connection
    if rtc.datetime()[4] == 3:
        if esp01.getConnectionStatus() not in ESP8266_WIFI_CONNECTED:
            connection = get_wifi_conn_status(connect_wifi())


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


def display_image(byte_array):
    # Load image into the framebuffer64)
    fb = framebuf.FrameBuffer(byte_array, fullscreen_px_x,fullscreen_px_y, framebuf.MONO_HLSB)
    # Clear oled display
    oled.fill(0)
    oled.blit(fb, 1, 1)
    oled.show()


def get_date_string(now):
    year = str(now[0])
    month = img_utils.months_dict[now[1]]
    day = str(now[2])
    day_of_wk = img_utils.days_dict[now[3]]
    return ''.join([day_of_wk, ', ', month, ' ', day, ', ', year])


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
    tens_hr_fb = framebuf.FrameBuffer(img_utils.num_ba_dict[tens_hr], digit_px_x, digit_px_y, framebuf.MONO_HLSB)
    ones_hr_fb = framebuf.FrameBuffer(img_utils.num_ba_dict[ones_hr], digit_px_x, digit_px_y, framebuf.MONO_HLSB)
    colon_fb = framebuf.FrameBuffer(img_utils.colon_ba, colon_px_x, digit_px_y, framebuf.MONO_HLSB)
    tens_min_fb = framebuf.FrameBuffer(img_utils.num_ba_dict[tens_min], digit_px_x, digit_px_y, framebuf.MONO_HLSB)
    ones_min_fb = framebuf.FrameBuffer(img_utils.num_ba_dict[ones_min], digit_px_x, digit_px_y, framebuf.MONO_HLSB)
    # add image chunks
    oled.blit(tens_hr_fb, tens_hr_digit_start_x, digit_start_y)
    oled.blit(ones_hr_fb, ones_hr_digit_start_x, digit_start_y)
    oled.blit(colon_fb, colon_start_x, digit_start_y)
    oled.blit(tens_min_fb, tens_min_digit_start_x, digit_start_y)
    oled.blit(ones_min_fb, ones_min_digit_start_x, digit_start_y)


style_func_list = [
    do_rainbow_cycle, do_chase, do_fill, do_off, do_red, 
    do_yellow, do_green, do_cyan, do_blue, do_purple, do_white,
    do_firefly, do_blend, do_flash
]
style_to_func_dict = dict(zip(led_style_list, style_func_list))
show_current_style(led_style)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_press_isr)
oled_timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
wifi_timer.init(period=wifi_check_per, mode=Timer.PERIODIC, callback=update_conn_status)
last_button_press = time()
while True:
    style_to_func_dict.get(led_style, do_rainbow_cycle)()