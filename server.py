#!/usr/bin/python
import os
import glob
import time
import json

from datetime import timedelta
from flask import Flask
from flask_cors import CORS, cross_origin
from Adafruit_PWM_Servo_Driver import PWM

app = Flask(__name__)
CORS(app)

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_str = lines[1][equals_pos+2:]
		temp_c = float(temp_str) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		temps = {}
		temps["c"] = temp_c
		temps["f"] = temp_f
		temps_json = json.dumps(temps)
		return temps_json

def get_uptime():
	with open('/proc/uptime', 'r') as f:
		uptime_sec = float(f.readline().split()[0])
		uptime_str = str(timedelta(seconds = uptime_sec))
	return uptime_str

@app.route("/")
def default():
	return "{\"online\":true}"

@app.route("/feed/")
def feed():
	pwm = PWM(0x40)
	pwm.setPWMFreq(50)

	pwm.setPWM(0, 0, 550)
	time.sleep(2)

	for x in range(0, 4):
		pwm.setPWM(0, 0, 128)
		time.sleep(0.5)
		pwm.setPWM(0, 0, 180)
		time.sleep(0.5)
	return "Feeding complete"

@app.route("/temp/")
def temp():
	return read_temp()

@app.route("/uptime/")
def uptime():
	return json.dumps(get_uptime())

if __name__ == "__main__":
	app.run(host='0.0.0.0')
