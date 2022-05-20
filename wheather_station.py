import pycom
import _thread
from machine import I2C
from network import WLAN
import machine
import time
from mqtt import MQTTClient
import CCS811
import BME280

#MQTT callback
def sub_cb(topic, msg):
   print(msg)

# if not connected to wifi, set machine as idle/inactive
while not wlan.isconnected():
    machine.idle()

# Connect to MQTT client in ubidots and connect 
# Use your token (accessed on Ubidots webpage) and leave password empty.
# Port is 1883 and device_id is found in config file.
client = MQTTClient("device_id", "industrial.api.ubidots.com",user="your_token", password="", port=1883)
client.set_callback(sub_cb)
client.connect()

############ define pins ############
#i2c ("Inter-Integrated Circuit") is the multi master bus used to connect the sensors to the lopy4
i2c = I2C(0)
i2c = I2C(0, I2C.MASTER)
i2c = I2C(0, pins=('P9', 'P10'))
i2c.init(I2C.MASTER, baudrate=10000)

ccs = CCS811.CCS811(i2c=i2c) # CCS811 is the gas sensor. Uses addr=90
bme = BME280.BME280(i2c=i2c) # BME280 is the pressure, humidity and outdoor temp sensor. Uses addr=119
adc = machine.ADC()
apin = adc.channel(pin='P16') # Analog indoor temperature sensor

# Outdoor sensors are running in a speparete thred to not interfear with the indoor temperature sensor, which needs
# to read values more often to detect high temperature values in case of a fire.
def outdoorThread():
    while True:
        if ccs.data_ready() :
            co2 = ccs.eCO2
            voc = ccs.tVOC
            temp = bme.temperature
            hum = bme.humidity
            pres = bme.pressure

            # Only when co2 is over 400, values will be sent to Ubidots
            if co2 > 400:
                client.publish("/v1.6/devices/WeatherStation", '{"CO2": ' + str(co2) +
                            ', "Temperature": ' + str(temp) +
                            ', "VOC": ' + str(voc) +
                            ', "Humidity": ' + str(hum) +
                            ', "Pressure": ' + str(pres) +'}')
            time.sleep(900)

# Start new thread
_thread.start_new_thread(outdoorThread, ())

# i, value to increment to know when to send valeus (only every 15 minutes if temperature is not higher than 50 degC)
i = 0
while True:
    millivolts = apin.voltage() # Analog temperature measured in millivolts
    degC = (millivolts - 500.0) / 10.0 # Convert millivolts to celsius

    # If temperature is higher than 50 degrees celsius or if i value is 900
    if(degC > 50 or i == 900):
        # Send values to Ubidots
        client.publish("/v1.6/devices/WeatherStation", '{"IndoorTemperature": ' + str(degC) +'}')
        i = 1 # Decrement i value to 1, to start count again, until reached 900
    else: i+=1
    time.sleep(1)