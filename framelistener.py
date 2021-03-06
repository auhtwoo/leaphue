import Leap
import math
import vmath
from collections import deque

from datetime import datetime


class FrameListener(Leap.Listener):

	def on_frame(self, controller):
		frame = controller.frame()

		self.confidence = frame.hands[0].confidence
		angle = 5*[None]

		if self.confidence < 0.1:
			self.avg_a = None
			return

		hd = frame.hands[0].direction
		self.hand_angle = vmath.angle_between((-1, 0, 0), (hd.x, hd.y, hd.z))
		self.handR = frame.hands[0].is_right
		self.handL = frame.hands[0].is_left
		#print self.handR
		for i, a in enumerate(self.angle_data):
			d = frame.hands[0].fingers[i].bone(2).direction
			angle[i] = math.pi/2 - vmath.angle_between((0, 1, 0), (d.x, d.y, d.z))
			#print angle[i]
			if i is 0:
				angle[i] += 0.2
			a.appendleft(angle[i])

		# find the finger pointing most downwards
		# and also the "second most downwards" finger.
		# if the difference between them is large enough we conclude
		# that one finger points downwards while the others don't.
		down_fingers = []
		down_fingers.append({'angle' : 0.0, 'finger_index' : -1})
		down_fingers.append({'angle' : 0.0, 'finger_index' : -1})
		for i in range(5):
		   if angle[i] > down_fingers[0]['angle']:
			   down_fingers[1] = down_fingers[0]
			   down_fingers[0] = {'angle' : angle[i], 'finger_index' : i}
		   elif angle[i] > down_fingers[1]['angle']:
			   down_fingers[1] = {'angle' : angle[i], 'finger_index' : i}

		angle_diff = down_fingers[0]['angle'] - down_fingers[1]['angle']
		
		if down_fingers[0]['finger_index'] != -1 and angle_diff > 0.4:
			self.finger_down = down_fingers[0]['finger_index']
		else:
			self.finger_down = None
		# We calculate average without the finger pointing downwards the most ...
		fingers_for_average = range(5)
		if down_fingers[0]['finger_index'] > -1:
			fingers_for_average.remove(down_fingers[0]['finger_index'])
		angle_sum = 0
		for i in fingers_for_average:
			angle_sum += angle[i]
		self.avg_a = angle_sum / 3.0
		#print self.avg_a
#		if self.avg_a is None:
#			self.finger_down = None
		#print self.finger_down
		if self.new_finger_down != self.finger_down:
			self.new_finger_down = self.finger_down
#		print self.
		

	def __init__(self):
		super(self.__class__, self).__init__()
		self.angle_data = []
		self.hand_angle = None
		self.handR = False
		self.handL = False
		# four fingers to keep track of
		for i in range(5):
			self.angle_data.append(deque([0] * 1000, 1000))
		self.confidence = 0
		self.avg_a = 0
		self.new_finger_down = None
		self.finger_down = None
		self.lastbri = []

	def pop_new_finger_down_if_any(self):
		finger = self.new_finger_down
		self.new_finger_down = None
		return finger

	def get_hand_direction(self):
		return self.hand_direction

	def get_confidence(self):
		return self.confidence

	# hand angle in relation to the eh, "left" vector, (-1, 0, 0).
	def get_hand_angle(self):
		return self.hand_angle

	def get_average_angle(self):
		return self.avg_a

	def get_angle_data(self):
		return self.angle_data

	def get_handR(self):
		return self.handR
		
	def get_handL(self):
		return self.handL
