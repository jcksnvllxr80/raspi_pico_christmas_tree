from machine import Pin
from utime import sleep_ms

button = Pin(15, Pin.IN, Pin.PULL_UP)
led = Pin(25, Pin.OUT)

while True:
  if button.value() == 0:
    led.on()
  else:
    led.off()
  # sleep_ms(100)
