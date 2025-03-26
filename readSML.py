#!/usr/bin/python3
# -*- coding: utf-8 -*-


#Fork for update to Python3
#Just to read out the values of "Wirkenergie_Summe_T1_T2_Wh" because I have no PIN

# USB device
usbdevice = "/dev/ttyUSB0"

# MQTT configuration
mqtt_username = "USERNAME"
mqtt_password = "PASSWORD"
mqtt_server = "HOSTNAME|IP-ADDRESS"
mqtt_server_port = 1883

import os
import time
import serial
import sys
import json
from threading import Timer
import paho.mqtt.client as mqtt

try:
	client = mqtt.Client(client_id="SML-python", clean_session=False)
except:
	try:
		client = mqtt.Client(client_id="SML-python", clean_session=False, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
	except:
		exit()


client.username_pw_set(username=mqtt_username, password=mqtt_password)
print("mqtt: User / Password set")

try:
	client.connect(mqtt_server, port=mqtt_server_port, keepalive=60)
	print("mqtt: Connected to server")
except:
	print("mqtt: Error connect to server")

try:
	client.loop_start()
	print("mqtt: Started loop")
except:
	print("mqtt: Error start loop")

time.sleep(4)


mystring = ""

#Checksumm will be back later

class Watchdog_timer:
	def __init__(self, timeout, userHandler=None):
		self.timeout = timeout
		self.handler = userHandler if userHandler is not None else self.defaultHandler
		self.timer = Timer(self.timeout, self.handler)
		self.timer.start()

	def reset(self):
		self.timer.cancel()
		self.timer = Timer(self.timeout, self.handler)
		self.timer.start()

	def stop(self):
		self.timer.cancel()

	def defaultHandler(self):
		raise self


def watchdogtimer_ovf():
	global mystring
	message = mystring[0:-2]

	if message[0:16] == '1b1b1b1b01010101':
		watchdog.stop()
		wirkenergie_Summe_T1_T2_Wh = round((int(message[132*2:(132 * 2 + 14)],16) / 10), 4)
		mystring=""
		#Just for "no Pin reading"
		client.publish("sml/ISKRA_MT681/Wirkenergie_Summe_T1_T2_Wh",str(wirkenergie_Summe_T1_T2_Wh))
		mystring=""
	else:
		mystring=""
		watchdog.stop()

time.sleep(10)

try:
	my_tty = serial.Serial(port=usbdevice, baudrate = 9600, parity =serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)
	my_tty.close()
	my_tty.open()

except:
	exit()

try:
	my_tty.reset_input_buffer()
	my_tty.reset_output_buffer()
	watchdog = Watchdog_timer(0.1, watchdogtimer_ovf)
	watchdog.stop()
	while True:
		while my_tty.in_waiting > 0:
			mystring += my_tty.readline().hex()
			watchdog.reset()

except KeyboardInterrupt:
	my_tty.close()
	client.loop_stop()
