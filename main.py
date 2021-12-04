# Example using PIO to drive a set of WS2812 LEDs.

import sys
from esp8266 import ESP8266
from machine import Pin, SPI, Timer, I2C, RTC
from EEPROM_24LC512 import EEPROM_24LC512
from ssd1306 import SSD1306_SPI
import framebuf
from utime import sleep_ms
import img_utils
from neopixel import Neopixel
import random
import base64
import ujson
import re

print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print("RPi-Pico MicroPython Ver:", sys.version)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

wifi_ssid = 'RkJJIFN1cnZlaWxsYW5jZSBWYW4gIzc='
wifi_pw = 'NHBwbDNzKzg0bm40bjQk'
TIME_URL = "worldtimeapi.org"
TIME_URL_PATH = "/api/timezone/America/New_York"
STYLE_BYTES = 2
STYLE_ADDRESS = 0
# Configure the number of WS2812 LEDs.
NUM_LEDS = 33
led_data_pin = Pin(22)
# configure wifi led pins for wifi user feedback
grn_wifi_led = Pin(10, Pin.OUT)
red_wifi_led = Pin(11, Pin.OUT)
brightness = 0.5
oled_fps = 5
wifi_check_freq = 0.017
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


def wifi_led_red():
    grn_wifi_led.off()
    red_wifi_led.on()


def wifi_led_green():
    red_wifi_led.off()
    grn_wifi_led.on()


connection = ""
wifi_led_red()
uart_port = 1
uart_tx_pin = 4
uart_rx_pin = 5
uart_baud = 115200


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
    conn_status = esp01.connectWiFi(
        base64.b64decode(bytes(wifi_ssid, 'utf-8')).decode("utf-8"),
        base64.b64decode(bytes(wifi_pw, 'utf-8')).decode("utf-8")
    )
    return get_wifi_conn_status(conn_status)


def get_wifi_conn_status(conn_status):
    if conn_status and "WIFI CONNECTED" in conn_status:
        wifi_led_green()
        # query_time_api()
        print("wifi connection --> {}".format(conn_status))
    else:
        wifi_led_red()
        print("sorry, cant connect to wifi AP! connection --> {}".format(conn_status))
    return conn_status


def set_rtc(re_match, response_json):
    date_formatted_str = re_match.group(0).replace("T", "-")\
        .replace(":", "-").replace(".", "-").split("-")
    time_list = list(map(int, date_formatted_str))
    RTC().datetime((
        time_list[0],
        time_list[1],
        time_list[2],
        int(response_json['day_of_week']),
        time_list[3],
        time_list[4],
        time_list[5],
        time_list[6]
    ))


def query_time_api():
    httpCode, httpRes = esp01.doHttpGet(TIME_URL, TIME_URL_PATH)
    if httpRes:
        print("\nResponse from {} --> {}\n".format(TIME_URL + TIME_URL_PATH, httpRes))
        json_resp_obj = ujson.loads(str(httpRes))
        print("json obj --> {}\n".format(json_resp_obj))
        datetime_regex_string = r'(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d)'
        match = re.search(datetime_regex_string, json_resp_obj['datetime'])
        if match:
            set_rtc(match, json_resp_obj)
            print("RTC was set from internet time API: {}!".format(match.group(0)))
        else:
            print("Error parsing time from http response; cant set RTC.")
    else:
        print("Error; no response from host: {}; cant set RTC."\
            .format(TIME_URL+TIME_URL_PATH))


# Create an SPI Object and use it for oled display
oled_timer = Timer()
wifi_timer = Timer()
# spi = SPI(0, 100000, mosi=mosi, sck=sck)
spi = SPI(0, 115200, mosi=mosi, sck=sck)
oled = SSD1306_SPI(pix_res_x, pix_res_y, spi, dc, rst, cs)
# Create an ESP8266 Object, init, and connect to wifi AP
esp01 = ESP8266(uart_port, uart_baud, uart_tx_pin, uart_rx_pin)
init_esp8266()
connection = connect_wifi()
print(esp01.getConnectionStatus())


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
led_string = Neopixel(led_data_pin, NUM_LEDS, brightness)


def color_chase(color, wait):
    for i in range(NUM_LEDS):
        led_string.pixels_set(i, color)
        sleep_ms(wait)
        led_string.pixels_show()
        if not led_style == "chase":
            break
    sleep_ms(20)


def update_oled_display(oled_timer):
    display_image(img_utils.get_img(led_style))


def update_conn_status(wifi_timer):
    global connection
    connection = get_wifi_conn_status(esp01.getConnectionStatus())


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
oled_timer.init(freq=oled_fps, mode=Timer.PERIODIC, callback=update_oled_display)
wifi_timer.init(freq=wifi_check_freq, mode=Timer.PERIODIC, callback=update_conn_status)
print(esp01.getConnectionStatus())
while True:
    pass
    style_to_func_dict.get(led_style, do_rainbow_cycle)()
