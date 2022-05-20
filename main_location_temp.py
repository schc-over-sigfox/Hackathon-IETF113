# import time
# from machine import UART
# import machine
# import os

# msg = ''
# # os.dupterm(None)
# # uart0 = UART(0, baudrate=115200)
# uart1 = UART(1, baudrate=9600)
# print("UART Ready")
# while True:
#     time.sleep(3)
#     msg = uart1.readline()
#     print(msg)
#     # uart0.write(str(msg))
# import machine
# import time
# import pycom
# import socket
# import struct
# import json
# from gps import GPS_UART_start
# from gps import NmeaParser


# rtc = machine.RTC()


# # def sendtoLoRa(s,  dev_ID,  place):
# #     # send some data

# #     dev_time = rtc.now()

# #     datatosend = struct.pack('ii', int(place.longitude*100000),  int(place.latitude*100000))
# #     print('LoRa send: {}\n'.format(datatosend))
# #     s.setblocking(True)
# #     s.send(datatosend)
# #     s.setblocking(False)

# #     pycom.rgbled(0x001f00)  # LoRa heartbeat LED on

# #     time.sleep(2)			# pause 2s for next read
# #     pycom.rgbled(0x00001f)  # LoRa heartbeat LED off


# def GPS_run():
#     print ('GPS_run')
#     pycom.heartbeat(False)      # turn off the heartbeat LED so that it can be reused
#     pycom.rgbled(0x000000)    # turn LED off
#     print('GPS start')

#     # f=open('device_name')   #get device name from file
#     # dev_ID = f.read()
#     # print(dev_ID)

#     # connect to GPS device
#     com = GPS_UART_start()

#     # initialize LoRa in LORA mode
#     # more params can also be given, like frequency, tx power and spreading factor
#     # print ("LoRa start")
#     # lora = LoRa(mode=LoRa.LORA,  frequency=925000000,  tx_power=20)

#     # create a raw LoRa socket
#     # s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

#     while True:
#         if (com.any()):
#             data =com.readline()
#             print (data)

#             if (data[0:6] == b'$GPGGA'):
#                 place = NmeaParser()
#                 place.update(data)
#                 print ("place", place.longitude,  ":",  place.latitude,  ":", place.fix_time)
#                 # sendtoLoRa(s,  dev_ID,  place)
   
#                 # f_log = open('Lora_log','a')  # careful that log file fills up the memory
#                 # f_log.write(data + ' ' + str(lora.rssi()) + '\n\n')
#                 # f_log.close()
#                 # wait a random amount of time
#                 time.sleep(10 + (machine.rng() & 0x3f)/10)
    

# print('Lora Run')
# GPS_run()

from cbor import loads, dumps




import pycom
from machine import UART, Pin
from micropyGPS import MicropyGPS
from dth import DTH
import time, json
# Setup the connection to your GPS here
# This example uses UART 3 with RX on pin Y10
# Baudrate is 9600bps, with the standard 8 bits, 1 stop bit, no parity
uart = UART(1,  pins=("P3",  "P4"),  baudrate=9600)
th = DTH(Pin('P9', mode=Pin.OPEN_DRAIN),0)
pycom.heartbeat(False)
pycom.rgbled(0x000008) # blue
time.sleep(2)
# Instatntiate the micropyGPS object
my_gps = MicropyGPS()
print("GPS Started!")
# Continuous Tests for characters available in the UART buffer, any characters are feed into the GPS
# object. When enough char are feed to represent a whole, valid sentence, stat is set as the name of the
# sentence and printed 41.421394166666667 2.1700635
location = {"lat":"", "long":"", "alt":""}
uploadData = {"temp":"", "hum":""}
while True:
    
    result = th.read()
    if result.is_valid():
        pycom.rgbled(0x001000) # green
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
        uploadData["temp"] = result.temperature
        uploadData["hum"] = result.humidity
    if uart.any():
        data = uart.read(1)
        # print(data.decode("utf-8"))
        stat = my_gps.update(data.decode("utf-8")) # Note the conversion to to chr, UART outputs ints normally
        if stat:
            print("stat")
            # print(stat)
            print(my_gps.latitude,my_gps.longitude,my_gps.course,my_gps.altitude,my_gps.date_string(),my_gps.time_since_fix())
            if my_gps.latitude and my_gps.longitude:
                if len(my_gps.latitude) == 3 and len(my_gps.longitude) == 3:
                    
                    lat = my_gps.latitude[0] + my_gps.latitude[1] / 60
                    uploadData["lat"] = lat if lat != 0 else 0
                    if my_gps.latitude[2] == "S":
                        uploadData["lat"] = -1 * lat if lat != 0 else 0
                    
                    long = my_gps.longitude[0] + my_gps.longitude[1] / 60
                    uploadData["long"] = long if long != 0 else 0
                    if my_gps.longitude[2] == "W":
                        uploadData["long"] = -1 * long if long != 0 else 0


                    uploadData["alt"] = my_gps.altitude if my_gps.altitude != 0 else 0
                    # print(my_gps.latitude[0])
                    # print(my_gps.latitude[1])
                    # print(my_gps.latitude[2])
                    # for d in my_gps.latitude:
                    #     print("d:{}".format(d))
            stat = None
            payload = bytearray(json.dumps(uploadData))
            print("payload:{}".format(len(payload)))
            coded = dumps(uploadData)
            print(coded, len(coded))

            decoded = loads(coded)
            print(decoded)
            print(uploadData)
            time.sleep(10)

            