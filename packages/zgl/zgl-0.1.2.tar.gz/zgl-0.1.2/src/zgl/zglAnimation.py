import time

class zglFadeObject:
	def __init__(self):
		self.alpha = 1.0
		self.fading_in = False
		self.fading_out = False
		self.fade_start_alpha = 1.0
		self.last_step_time = 0
		self.fade_in_delay = 0.0
		self.fade_in_time = 0.250		# in seconds
		self.fade_out_delay = 0.0
		self.fade_out_time = 0.250

	def fadeIn(self, t=time.time()):
		self.fading_in = True
		self.fading_out = False
		self.last_step_time = t + self.fade_in_delay

	def fadeOut(self, t=time.time()):
		self.fading_in = False
		self.fading_out = True
		self.last_step_time = t + self.fade_out_delay

	# time should be passed in to ensure the animation on each frame
	# are synchronized in terms of time
	def stepFade(self, t):
		if self.fading_in and t > self.last_step_time:
			d_time = t - self.last_step_time
			self.alpha += d_time/self.fade_in_time
			if self.alpha > 1.0:
				self.alpha = 1.0
				self.fading_in = False
			self.last_step_time = t
		elif self.fading_out and t > self.last_step_time:
			d_time = t - self.last_step_time
			self.alpha -= d_time/self.fade_out_time
			if self.alpha < 0.0:
				self.alpha = 0.0
				self.fading_out = True
			self.last_step_time = t
