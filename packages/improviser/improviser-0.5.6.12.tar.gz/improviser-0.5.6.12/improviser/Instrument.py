from mingus.extra import fluidsynth
from mingus.containers.Note import Note
from random import randrange

class Instrument:

	history = []
	params = {}

	
	playing = []
	last_played = []
	last_chan= 0

	start = 0
	end = -1
	step = 0
	midi_set = False
	
	def __init__(self, parameters):
		self.params = parameters
		if 'start' in parameters:
			self.start = self.params["start"]
			if 'end' not in parameters:
				if 'step' in parameters:
					self.end = self.start + parameters["step"]
		if 'end' in parameters:
			self.end= self.params["end"]

		if 'step' in parameters:
			self.step = parameters["step"]

	def play(self, state):
		
		if not(self.midi_set) and 'midi_instr' in self.params:
			fluidsynth.midi.set_instrument(self.params["channel"], self.params["midi_instr"])
			self.midi_set = True

			
		if 'let_ring' not in self.params:
			self.stop_playing_notes()
		else:
			if not self.params['let_ring']:
				self.stop_playing_notes()


		if 'channel' in self.params:
			n = self.generate_note(state)
			v = self.generate_velocity(state)
			if n != None:
				fluidsynth.play_NoteContainer(n, v, \
					self.params["channel"])
				self.last_chan = self.params["channel"]
				self.playing += n
				self.last_played = n
				if state["paint_function"] != None:
					state["paint_function"](n, self.params["channel"])


	def generate_note(self, state):
		return None

	def generate_velocity(self, state):
		wild, minv, maxv = 1.0, 50, 100
		if 'max_velocity' in self.params:
			maxv = self.params['max_velocity']
		if 'min_velocity' in self.params:
			minv = self.params['min_velocity']
		if 'wild' in state:
			wild = state['wild']

		if state["tick"] % (state["resolution"] / float(state["meter"][1])) == 0:
			velocity = randrange(maxv - 10, maxv)
		else:
			velocity = randrange(minv, maxv)

		wildness = (minv - maxv) / 2 * wild
		return max(min(velocity - wildness, 127), 0)


	def stop_playing_notes(self):
		fluidsynth.stop_NoteContainer(self.playing,
				self.last_chan)
		self.playing = []
