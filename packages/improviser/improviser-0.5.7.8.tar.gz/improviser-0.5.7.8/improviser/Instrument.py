from mingus.midi import fluidsynth
from mingus.containers.Note import Note
from random import randrange
from mingus.containers.Track import Track
from mingus.containers.Bar import Bar
from mingus.containers.Instrument import MidiInstrument

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
	last_tick = (-1, -1) # iteration, tick
	
	def __init__(self, parameters):
		self.track = Track()
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

	def add_rest(self, state):
		if state["tick"] == 0:
			if hasattr(self, "bar"):
				self.track + self.bar
			b = Bar()
			b.set_meter(state["meter"])
			b.key = state["key"]
			self.bar = b

		if len(self.bar) > 0:
			if self.bar[0][2] is None:
				i = 1 / (1.0 / state["resolution"] + \
					1.0 / self.bar[0][1])
				self.bar[0][1] = i
			else:
				self.bar.place_notes(None, state["resolution"])
		else:
			self.bar.place_notes(None, state["resolution"])
		self.last_tick = (state["iterations"], state["tick"])


	def play(self, state):
		if not(self.midi_set) and 'midi_instr' in self.params:
			if not self.no_fluidsynth:
				fluidsynth.set_instrument(self.params["channel"], self.params["midi_instr"])
			self.midi_set = True
			i = MidiInstrument()
			i.instrument_nr = self.params["midi_instr"]
			self.track.instrument = i

		if state["tick"] == 0:
			if hasattr(self, "bar"):
				self.track + self.bar
			b = Bar()
			b.set_meter(state["meter"])
			b.key = state["key"]
			self.bar = b
		let_ring = False
		#if 'let_ring' not in self.params:
		self.stop_playing_notes()
		#else:
		#	if not self.params['let_ring']:
		#		self.stop_playing_notes()
		#	else:
		#		let_ring = True


		n = self.generate_note(state)
		v = self.generate_velocity(state)
		if n is not None and n != []:
			for note in n:
				note.velocity = int(v)
				note.channel = self.params["channel"]

			# Record played notes in a Track
			if self.last_tick != (state["iterations"], state["tick"]):
				self.bar.place_notes(n, state["resolution"])
			else:
				self.bar.bar[-1][2].add_notes(n)

			if not self.no_fluidsynth:
				fluidsynth.play_NoteContainer(n,
					self.params["channel"], v)
			self.last_chan = self.params["channel"]
			self.playing += n
			self.last_played = n
			if state["paint_function"] != None:
				state["paint_function"](n, self.params["channel"])
		else:
			if len(self.bar) > 0:
				if self.bar[-1][1] is None:
					i = 1 / (1.0 / state["resolution"] + \
						1.0 / self.bar[-1][1])
					self.bar[-1][1] = i
				else:
					self.bar.place_notes(None, state["resolution"])
			else:
				self.bar.place_notes(None, state["resolution"])

		self.last_tick = (state["iterations"], state["tick"])



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
		if not self.no_fluidsynth:
			fluidsynth.stop_NoteContainer(self.playing,
				self.last_chan)
		self.playing = []
