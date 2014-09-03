#!/usr/bin/env python3

__email__ = 'mad_dev@linuxmail.org'
import pifacedigitalio as pf
import time
import subprocess
import urllib
from xml.dom import minidom

def get_temp(cc):
	##Thanks to http://stackoverflow.com/questions/16070885/python-yahoo-weather-xml-parse-works-with-2-7-1-but-not-2-6-1
	CITY_ID = cc
	TEMP_TYPE = 'c'

	WEATHER_URL = 'http://xml.weather.yahoo.com/forecastrss?w=' + CITY_ID +' &u=' + TEMP_TYPE
	WEATHER_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0'

	dom = minidom.parse(urllib.urlopen(WEATHER_URL))
	ycondition = dom.getElementsByTagNameNS(WEATHER_NS, 'condition')[0]
	CURRENT_OUTDOOR_TEMP = ycondition.getAttribute('temp')
	return CURRENT_OUTDOOR_TEMP

def switch_control():
	'''You can think of this a virtual toggle switch.
	   The value for ON and OFF is 1(one)
	   I am not sure why, but I am assuming it is due to the method of wiring(IC pin)
	   
	   The initial state is imperative for the operation. e.g. If the remote is on, the switch will close it.
	'''
	pfd = pf.PiFaceDigital()
	pfd.relays[1].value = 0
	time.sleep(0.7) #I read somewhere that it is not recommended to switch the relay immediately 
	pfd.relays[1].value = 1

def run():
	cc = '721943' #Example Rome http://weather.yahoo.com/italy/lazio/rome-721943/
	start = '18'
	stop = '17'
	state = remember()
	print('The Current State is '+state)
	print('Based on Yahoo! Outdoor Temp = %s C\n' %get_temp(cc))
	if get_temp(cc) >= start:
		print('Temp is at start range [%s]' %start)
		if 'on' in state:
			print('AC is on') #Not the actual AC, rather the remote
			pass
		elif 'off' in state:
			print('Starting...')
			switch_control()
			b = open('state', 'w+')
			b.write('on')
			b.close()

	if get_temp(cc) <= stop:
		print('Temp is at stop range [%s]' %stop)
		if 'off' in state:
			print('AC is off')
			pass
		elif 'on' in state:
			print('Stopping')
			switch_control()
			b = open('state', 'w+')
                        b.write('off')  
                        b.close()
	else:
		pass

def remember():
	'''You need to enter the first state manually
	   1- on
	   2- off
	'''
	a = open('state', 'r')
	state = a.read()
	a.close()
	return state
	
run()
