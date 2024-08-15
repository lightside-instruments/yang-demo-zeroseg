#!/usr/bin/env python

import time
import sys, os
import argparse
import yangcli
from lxml import etree
import yangrpc
import ZeroSeg.led as led
#import I2C_LCD_driver
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

	print("Connected ..")
	time.sleep(1)

#	mylcd = I2C_LCD_driver.lcd()

	zeroseg_led = led.sevensegment(cascaded=2)
	remote_conn = {}
	while(1):

		result = yangcli.yangcli(conn, "xget /line-display")
		print(etree.tostring(result))
		text = result.xpath('./data/line-display/text')
		instance_id = result.xpath('./data/line-display/instance-id')
		remote_instance_id = result.xpath('./data/line-display/remote-instance-id')

		if(len(text)==1):
			print(text[0].text)
			zeroseg_led.write_text(1,text[0].text)
#			mylcd.lcd_clear()
#			mylcd.lcd_display_string(text[0].text, 1)

		elif(len(instance_id)==1):
			print(instance_id[0].text)
			update_interval = result.xpath('./data/line-display/update-interval')
			print(instance_id[0].text)
			result2 = yangcli.yangcli(conn, "xget %s"%(instance_id[0].text))
			text = result2.xpath('./data/%s'%(instance_id[0].text))
			if(len(text)==1):

				print(text[0].text)
#				mylcd.lcd_clear()
#				mylcd.lcd_display_string(instance_id[0].text[-16:], 1)
#				mylcd.lcd_display_string(text[0].text, 2)
				zeroseg_led.write_text(1,text[0].text)
			else:
				print("")

		elif(len(remote_instance_id)==1):
			update_interval = result.xpath('./data/line-display/update-interval')
			remote_address = result.xpath('./data/line-display/remote-netconf/ssh/tcp-client-parameters/remote-address')[0].text;
			remote_port = result.xpath('./data/line-display/remote-netconf/ssh/tcp-client-parameters/remote-port')[0].text;
			remote_ssh_username = result.xpath('./data/line-display/remote-netconf/ssh/ssh-client-parameters/client-identity/username')[0].text;
			remote_ssh_password = result.xpath('./data/line-display/remote-netconf/ssh/ssh-client-parameters/client-identity/password/cleartext-password')[0].text;
			remote_instance_id = result.xpath('./data/line-display/remote-instance-id')[0].text;


			if(not remote_conn or
                           remote_address!=prev_remote_address or
                           remote_port!=prev_remote_port or
                           remote_ssh_username!=prev_remote_ssh_username or
                           remote_ssh_password!=prev_remote_ssh_password):
				remote_conn = yangrpc.connect(remote_address, int(remote_port), remote_ssh_username, remote_ssh_password, os.getenv('HOME')+"/.ssh/id_rsa.pub", os.getenv('HOME')+"/.ssh/id_rsa")
				if(remote_conn==None):
					print("Error: yangrpc failed to connect!")
					time.sleep(1)
					continue
				else:
					print("Connected to remote ...")

			result2 = yangcli.yangcli(remote_conn, "xget %s"%(remote_instance_id))
			text = result2.xpath('./data/%s'%(remote_instance_id))

			print(text[0].text)

			prev_remote_address = remote_address
			prev_remote_port = remote_port
			prev_remote_ssh_username = remote_ssh_username
			prev_remote_ssh_password = remote_ssh_password

#			mylcd.lcd_clear()
#			mylcd.lcd_display_string(instance_id[0].text[-16:], 1)
#			mylcd.lcd_display_string(text[0].text, 2)

		time.sleep(1)

	return(0)
sys.exit(main())
