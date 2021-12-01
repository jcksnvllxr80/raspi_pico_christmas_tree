from machine import I2C, Pin
from EEPROM_24LC512 import EEPROM_24LC512

INT_BYTES = 4

sda = Pin(12)
scl = Pin(13)
i2c = I2C(0, sda=sda, scl=scl, freq=1000000)
i2c_devices = i2c.scan()
print("I2C Devices: ")
print(i2c_devices)

eeprom = EEPROM_24LC512(i2c, i2c_devices[0])

style_address = 0
style_index = 1
eeprom.write(style_address, style_index)
stored_style_index = eeprom.read(style_address, INT_BYTES)
print(stored_style_index)
