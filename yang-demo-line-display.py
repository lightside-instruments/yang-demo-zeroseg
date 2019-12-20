#!/usr/bin/env python

import time
import sys, os
import argparse
from yangcli import yangcli
from lxml import etree
import yangrpc
#import ZeroSeg.led as led
import I2C_LCD_driver
#from time import *

def main():
	print("""
#Description: Connects and updates the display according to the configuration.
#Procedure:
#1 - Open session.
#2 - Loop reading configuration and displaying text.
""")

	parser = argparse.ArgumentParser()
	parser.add_argument("--server", help="server name e.g. 127.0.0.1 or server.com (127.0.0.1 if not specified)")
	parser.add_argument("--user", help="username e.g. admin ($USER if not specified)")
	parser.add_argument("--port", help="port e.g. 830 (830 if not specified)")
	parser.add_argument("--password", help="password e.g. mypass123 (passwordless if not specified)")

	args = parser.parse_args()

	if(args.server==None or args.server==""):
		server="127.0.0.1"
	else:
		server=args.server

	if(args.port==None or args.port==""):
		port=830
	else:
		port=int(args.port)

	if(args.user==None or args.user==""):
		user=os.getenv('USER')
	else:
		user=args.user

	if(args.password==None or args.password==""):
		password=None
	else:
		password=args.password

	conn = yangrpc.connect(server, port, user, password, os.getenv('HOME')+"/.ssh/id_rsa.pub", os.getenv('HOME')+"/.ssh/id_rsa")
	if(conn==None):
		print("Error: yangrpc failed to connect!")
		return(-1)

	time.sleep(1)

	mylcd = I2C_LCD_driver.lcd()

	#zeroseg_led = led.sevensegment(cascaded=2)
	while(1):

		result = yangcli(conn, "xget /line-display")
		text = result.xpath('./data/line-display/text')
		if(len(text)!=1):
			instance_id = result.xpath('./data/line-display/instance-id')
			if(len(instance_id)==1):
				print instance_id[0].text
				update_interval = result.xpath('./data/line-display/update-interval')
				result2 = yangcli(conn, "xget %s"%(instance_id[0].text))
				text = result2.xpath('./data/%s'%(instance_id[0].text))
				mylcd.lcd_clear()
				mylcd.lcd_display_string(instance_id[0].text[-16:], 1)
				mylcd.lcd_display_string(text[0].text, 2)


		else:
			print text[0].text
			#zeroseg_led.write_text(1,text[0].text)
			mylcd.lcd_clear()
			mylcd.lcd_display_string(text[0].text, 1)
		time.sleep(1)

	return(0)
sys.exit(main())
