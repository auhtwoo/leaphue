from __future__ import print_function
from phue import Bridge
from threading import Thread
import time
from rgb_cie import ColorHelper
import numpy as np

class HueController:
#12345 = left middle corner desk right
	BRIDGE_IP = '192.168.2.148'
	
	def __init__(self, frame_listener):
		def lamp_controller():
			try:
				while True:
					time.sleep(0.1 + self.sleep)
					self.confidence = self.frame_listener.get_confidence()
					if self.confidence > 0.98:
						hand_angle = self.frame_listener.get_hand_angle()
						#thumb all lights off, 1 desk, 2 all overhead 3 switch between overhead 4 corner
						changed = True
						new_finger_down = self.frame_listener.pop_new_finger_down_if_any()
						if self.frame_listener.get_handR():
							self.hand = 1
						elif self.frame_listener.get_handL():
							self.hand = 2
						if new_finger_down != self.last_finger:
							changed = True
						if self.frame_listener.get_handR() and new_finger_down != None:
							if new_finger_down is 0:
								self.current_lamp = 0 #all lamps
							elif new_finger_down is 1:
								self.current_lamp = 3 #desk
							elif new_finger_down is 2:
								self.current_lamp = 6 #overheads
							elif new_finger_down is 4:
								self.current_lamp = 4 #corner
							elif new_finger_down is 3:
								self.olight += 1
								if self.olight > 2:
									self.olight = 0
								self.current_lamp = self.olights[self.olight]
							if new_finger_down != None:
								#self.current_lamp = new_finger_down+1
								if self.current_lamp != self.prev_lamp:
									#print "lamp"
									#print self.current_lamp
									if self.current_lamp is 0:
										for i in range(1,6):
											self.last_on_arr[i-1] = b.get_light(i,'on')
										self.on = False
									elif self.current_lamp is 6:
										self.on = True
									else:
										self.on = b.get_light(self.current_lamp, 'on')
									self.flash_lights(b)
								elif new_finger_down != self.last_finger:
									if self.on:
										self.on = False
										#print "off"
									else:
										self.on = True
										#print "on"
						elif self.frame_listener.get_handL() and new_finger_down != None:#4 toggle, 0 change color, 3 reset, 2 down 1 up
							if new_finger_down is 3:
								self.bright += 1
								if self.bright > 2:
									self.bright = 0
								if self.bri is 145 and self.on is True:
									changed = False
								self.bri = 145
								#print self.bri
								self.on = True
							elif new_finger_down is 2:
								self.bri = self.bri-10
								if self.bri < 1:
									self.bri = 1
								#print self.bri
								self.on = True
							elif new_finger_down is 1:
								self.bri = self.bri+10
								if self.bri > 255:
									self.bri = 255
								#print self.bri
								self.on = True
							elif new_finger_down is 0 and self.last_finger != 0:
								self.color = 1 ^ self.color
								self.on = True
							elif new_finger_down is 4 and self.last_finger != 4:
								if self.on:
									self.on = False
								#	print "off"
								else:
									self.on = True
								#	print "on"
						else:
							new_finger_down = None
					else:
						changed = True
						new_finger_down = None
						
						if self.confidence > 0.9:
							if self.frame_listener.get_handR():
								print("Detecting right hand")
							elif self.frame_listener.get_handL():
								print("Detecting left hand")
						else:
							self.hand = -1
						
					if self.last_hand is self.hand and self.last_finger is new_finger_down and self.prev_lamp is self.current_lamp and self.last_on is self.on and self.last_bri is self.bri:
						changed = False
					#print(self.confidence)
					self.last_finger = new_finger_down
					self.upd_lights(b,changed)
					self.last_hand = self.hand
					self.prev_lamp = self.current_lamp
					self.last_on = self.on
					self.last_bri = self.bri
			except KeyboardInterrupt:
				print("rip")

		self.current_lamp = 3
		self.prev_lamp = 3
		self.last_finger = None
		self.bri = 145
		self.last_bri = 145
		self.color = 1
		self.confidence = 0.0
		self.bright = 1
		self.on = True
		self.hand = 0
		self.last_hand = 0
		self.last_on = True
		self.sleep = 0
		self.olights = [1,2,5]
		self.olight = 0
		self.last_on_arr = [False,False,False,False,False]
		self.lastangle = 0.0
		self.fingers = ["Thumb","Index finger","Middle finger","Ring finger","Pinky"]
		self.str_on = ["on","off"]
		self.str_col = ["white","yellow tint"]
		self.str_hand = ["right","left"]
		self.str_lamp = ["All lamps","Left lamp","Middle lamp","Desk lamp","Corner lamp","Right lamp","Overhead lamps"]
		self.frame_listener = frame_listener
		b = Bridge(self.BRIDGE_IP)
		b.connect()
		self.colors = [(255,255,255), (255, 200, 0), (150,150,150), (222,222,222)]
		self.brights = [50,145,220]
		Thread(target=lamp_controller).start()

	def get_current_brightness(self):
		# roughly go between ranges [1, 0] to [0, 255]
		angle = self.frame_listener.get_average_angle()
		if self.frame_listener.get_confidence() == 0 or angle is None:
		#	print self.frame_listener.get_confidence()
			return self.lastangle
		self.lastangle = int(min(255, 255.0*min(1.0, max(0.0, -angle + 0.5))))
		#print self.lastangle
		return self.lastangle

	def flash_lights(self, b):
		if self.current_lamp is 0:
			for i in range (1,6):
				if b.get_light(i, 'on'):
					b.set_light(i, 'on', False)
					time.sleep(0.25)
					b.set_light(i, 'on', True)
		elif self.current_lamp is 6:
			for i in self.olights:
				if b.get_light(i, 'on'):
					b.set_light(i, 'on', False)
					time.sleep(0.25)
					b.set_light(i, 'on', True)
		else:
			b.set_light(self.current_lamp, 'on', False)
			time.sleep(0.25)
			b.set_light(self.current_lamp, 'on', True)
			
	def upd_lights(self, b, changed):
		temp = ""
		if self.last_on != self.on:
			temp += " " + self.str_on[self.last_on]
		if self.last_bri != self.bri or self.last_on != self.on:
			temp += " to brightness " + str(100*(float(self.bri)/255)) + "% "
		if self.hand is 2 and self.last_finger is 0:
			temp += " color " + self.str_col[self.color]
		if self.last_finger is None and self.hand > -1:
			temp = "All fingers up " + temp
		elif self.hand is 1:
			temp = "Right hand " + self.fingers[self.last_finger] + " selecting " + self.str_lamp[self.current_lamp] + temp
		elif self.hand is 2:
			temp = "Left hand " + self.fingers[self.last_finger] + " setting " + self.str_lamp[self.current_lamp] + temp
		elif self.hand is -1:
			temp = "Hand removed"

		if changed:
			print(temp)
		if self.current_lamp < 6 and self.current_lamp > 0:
			b.set_light(self.current_lamp, 'on', self.on)
			if self.on:
				b.set_light(self.current_lamp, 'bri', self.bri)
				b.lights[self.current_lamp -1].xy = ColorHelper().getXYPointFromRGB(*self.colors[self.color])
		elif self.current_lamp is 0:
			for i in range (1,6):
				if self.on:
					if self.last_on_arr[i-1] is True:
						b.set_light(i, 'on', True)
				else:
					b.set_light(i, 'on', False)
		elif self.current_lamp is 6:
			for i in self.olights:
				b.set_light(i, 'on', self.on)
				if self.on:
					b.set_light(i, 'bri', self.bri)
					b.lights[i -1].xy = ColorHelper().getXYPointFromRGB(*self.colors[self.color])
