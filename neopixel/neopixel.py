import array
from utime import sleep_ms
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)[T3 - 1]
    jmp(not_x, "do_zero")   .side(1)[T1 - 1]
    jmp("bitloop")          .side(1)[T2 - 1]
    label("do_zero")
    nop()                   .side(0)[T2 - 1]
    wrap()


class Neopixel:
    BLACK = (0, 0, 0)
    RED = (0, 255, 0)
    YELLOW = (150, 255, 0)
    GREEN = (255, 0, 0)
    CYAN = (255, 0, 255)
    BLUE = (0, 0, 255)
    PURPLE = (0, 180, 255)
    WHITE = (255, 255, 255)
    COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

    FIREFLY_COLORS = [
        (232, 100, 255),  # Purple
        (200, 200, 20),  # Yellow
        (30, 200, 200),  # Blue
        (150, 50, 10),
        (50, 200, 10)
    ]

    def get_colors(self):
        return self.COLORS


    def get_firefly_colors(self):
        return self.FIREFLY_COLORS


    def __init__(self, data_pin, num_leds, brightness):
        self._brightness = brightness
        self.num_leds = num_leds
        self.data_pin = data_pin
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=self.data_pin)
        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)
        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num_leds)])


    @property  # getter
    def brightness(self):
        return self._brightness


    @brightness.setter  # setter
    def brightness(self, brightness):
        if brightness < 0.1:
            brightness = 0.1
        if brightness > 1.0:
            brightness = 1.0
        self._brightness = brightness


    def clear_pixels(self):
        self.pixels_fill((0, 0, 0))


    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num_leds)])
        for i, c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g << 16) + (r << 8) + b
        self.sm.put(dimmer_ar, 8)
        sleep_ms(10)

    def pixels_set(self, i, color):
        self.ar[i] = (color[1] << 16) + (color[0] << 8) + color[2]


    def pixels_fill(self, color):
        for i in range(len(self.ar)):
            self.pixels_set(i, color)


    @staticmethod
    def colorHSV(hue, sat, val):
        if hue >= 65536:
            hue %= 65536

        hue = (hue * 1530 + 32768) // 65536
        if hue < 510:
            b = 0
            if hue < 255:
                r = 255
                g = hue
            else:
                r = 510 - hue
                g = 255
        elif hue < 1020:
            r = 0
            if hue < 765:
                g = 255
                b = hue - 510
            else:
                g = 1020 - hue
                b = 255
        elif hue < 1530:
            g = 0
            if hue < 1275:
                r = hue - 1020
                b = 255
            else:
                r = 255
                b = 1530 - hue
        else:
            r = 255
            g = 0
            b = 0

        v1 = 1 + val
        s1 = 1 + sat
        s2 = 255 - sat
        r = ((((r * s1) >> 8) + s2) * v1) >> 8
        g = ((((g * s1) >> 8) + s2) * v1) >> 8
        b = ((((b * s1) >> 8) + s2) * v1) >> 8
        return r, g, b


    @staticmethod
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