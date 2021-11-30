# Raspberry Pi Pico Examples 

## Drive a set of fifty (50) WS2812 LEDs.
- Use a micropython IDE to upload the script file, examples/led_strip/main.py, to the pico and connect 3 pins to the light strip
  - data --> GPIO22
  - vcc  --> vcc
  - gnd  --> gnd

## Text Image Creation
  1. open paint and set the properties canvas size to the number of pixels on the display (128,64)
  2. add some text with cool font and different size as well as bold and get it centered in the canvas
  3. select all (ctrl+a) then right click the image and invert colors
  4. save the image to a place easy to get to
  5. got to https://javl.github.io/image2cpp/ and open the image from the previous step
  6. convert it and then use the *_img files in this proj as a template on how to use that data