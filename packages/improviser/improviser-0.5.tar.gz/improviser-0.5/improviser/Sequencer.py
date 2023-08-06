from mingus.core import progressions, diatonic
from mingus.containers.NoteContainer import NoteContainer
from time import sleep
from random import random
from mingus.core import chords

class Sequencer:

	instruments = []
	progression = []
	key = 'E'
	tick_length = 0.5
	meter = (4,4)
	iterations = 0
	play_iterations = 32
	swing = True
	wild = 0.4

	def __init__(self, song):
		self.block = song
		self.load_from_block()
		self.reset_state()


	def add_instrument(self, instr):
		self.instruments.append(instr)


	def load_from_block(self):
		self.progression = self.block.get_progression(self.iterations)
		self.resolution = self.block.get_resolution(self.iterations)
		self.instruments = self.block.get_instruments(self.iterations)
		self.set_bpm(self.block.get_bpm(self.iterations))

	def play_instruments(self):

		for instr in self.instruments:
			if self.iterations >= instr.start and \
				(self.iterations < instr.end \
				 or instr.end == -1):
				instr.play(self.state)
			elif self.iterations == instr.end and \
					instr.step != 0:
				diff = instr.end - instr.start
				instr.start = instr.end + instr.step
				instr.end = instr.start + diff


	def play(self):
		self.chords = progressions.to_chords(self.progression, self.key)
		self.state["chords"] = self.chords

		i = 0
		ticks = self.resolution / self.meter[1] * self.meter[0]
		while i < len(self.chords) * ticks:
			chord = self.chords[ i / ticks ]

			if chord != self.state["chord"]:
				print chords.determine(chord)[0]
				self.state["scale"] = diatonic.get_notes(self.key)
				for note in chord:
					if note not in self.state["scale"]:
						self.replace_scale_note(note)
			self.state["chord"] = chord
			self.state["progression_index"] = i / self.resolution
			self.state["tick"] = i % ticks
			self.state["ticks"] = ticks
			self.state["iteration_tick"] = i
			self.state["wild"] = self.wild
				
			self.play_instruments()
			if not self.swing:
				sleep(self.tick_length)
			else:
				if i % 2 == 0:
					sleep(self.tick_length * 1.33)
				else:
					sleep(self.tick_length * 0.66)

			self.set_bpm(self.block.get_bpm(self.iterations))
			i += 1

		
		if self.play_iterations != 1:
			print "-" * 20
			self.iterations += 1
			self.play_iterations -= 1
			self.load_from_block()
			self.reset_state()
			return self.play()
		else:
			return self.simple_ending()

	def simple_ending(self):
		self.state["chord"] = self.chords[0]
		self.state["tick"] = 0
		self.state["iteration_tick"] = 0
		self.state["progression_index"] = 0
		self.state["wild"] = 1.0
		self.play_instruments()
		sleep(self.tick_length * 10)
		self.stop()

	def replace_scale_note(self, note):
		s = self.state["scale"]
		for n in s:
			if n[0] == note[0]:
				s[ s.index(n) ] = note
				return
		s.append(note)

	def reset_state(self):
		self.state = {
			'chord': [],
			'chords': [], 
			'progression': self.progression, 
			'progression_index': 0, 
			'bpm': self.bpm, 
			'tick': 0, 
			'meter': self.meter, 
			'resolution': self.resolution, 
			'key': self.key,
			'scale': diatonic.get_notes(self.key), 
			'wild': self.wild,

			}


	def set_bpm(self, bpm):
		self.bpm = bpm
		self.tick_length = (60.0 / bpm) / (self.resolution / \
				self.meter[1])


	def set_progression(self, progression):
		self.progression = progression


	def stop(self):
		for instr in self.instruments:
			instr.stop_playing_notes()
