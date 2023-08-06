from mingus.core import progressions, diatonic
from mingus.containers.NoteContainer import NoteContainer
from time import sleep, time
from random import random
from mingus.core import chords

class Sequencer:

	instruments = []
	progression = []
	state = {}
	iterations = 0
	play_iterations = 1000
	paint_function = None
	refresh_function = None
	update_function = None
	verbose = False

	def __init__(self, block):
		self.block = block
		self.iteration()

	def block_iteration(self):
		"""Queries the block class for information """
		"""each time a progression has played."""

		b = self.block
		self.meter = b.get_meter(self.iterations, 0)
		self.key = b.get_key(self.iterations)
		self.progression = b.get_progression(self.iterations)
		self.resolution = b.get_resolution(self.iterations)
		self.instruments = b.get_instruments(self.iterations)
		self.set_bpm(b.get_bpm(self.iterations, 0))
		self.wild = b.get_wildness(self.iterations, 0)
		self.reset_state()
	
	def block_tick(self):
		"""Queries the block class on every tick."""

		self.sync()
		b = self.block
		self.set_bpm(b.get_bpm(self.iterations, self.tick))
		self.meter = b.get_meter(self.iterations, self.tick)
		self.wild = b.get_wildness(self.iterations, self.tick)

	def change_scale(self):
		
		if self.chord != self.state["chord"]:
			if self.verbose:
				print chords.determine(self.chord)[0]
			self.state["scale"] = \
				diatonic.get_notes(self.key)
			for n in self.chord:
				if n not in self.state["scale"]:
					self.replace_scale_note(n)

	def change_state(self, tick):

		self.change_scale()
		self.tick = tick % self.ticks
		self.state["chord"] = self.chord
		self.state["progression_index"] = tick / self.resolution
		self.state["tick"] = self.tick
		self.state["ticks"] = self.ticks
		self.state["iteration_tick"] = tick
		self.state["wild"] = self.wild
		self.state["paint_function"] = self.paint_function


	def iteration(self):
		"""Gets called each iteration -- when self.progression """
		"""changes or gets repeated."""
		if self.verbose:
			print "-" * 20
		self.iterations += 1
		self.play_iterations -= 1
		self.block_iteration()
		self.chords = progressions.to_chords( \
				self.progression, self.key)
		self.state["chords"] = self.chords
		self.ticks = self.resolution / self.meter[1] \
				* self.meter[0]


	def play_instruments(self):
		"""Plays all the instruments in self.instruments if """
		"""they are currently enabled."""
		
		it = self.iterations
		for i in self.instruments:
			if it >= i.start and (it < i.end or i.end == -1):
				i.play(self.state)
			elif it == i.end and i.step != 0:
				diff = i.end - i.start
				i.start = i.end + i.step
				i.end = i.start + diff


	def play(self):
		"""Loops until self.play_iterations iterations """
		"""have been played."""

		while self.play_iterations >= 0:
			i = 0
			while i < len(self.chords) * self.ticks:

				self.tick_start = time()
				self.chord = self.chords[ i / self.ticks ]

				if self.refresh_function != None:
					self.refresh_function()
				
				self.change_state(i)
				self.play_instruments()

				if self.update_function != None:
					self.update_function()

				self.block_tick()
				i += 1
		
			self.iteration()
		self.simple_ending()

	def simple_ending(self):
		chord = self.chords[0]
		self.reset_state()
		self.state["chord"] = chord
		self.state["ticks"] = self.ticks
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
			'iteration_tick': 0,
			'bpm': self.bpm, 
			'tick': 0, 
			'meter': self.meter, 
			'resolution': self.resolution, 
			'key': self.key,
			'scale': diatonic.get_notes(self.key), 
			'wild': self.block.get_wildness(0,0),
			'refresh_function': self.refresh_function,
			'paint_function': self.paint_function,
			'update_function': self.update_function,

			}


	def set_bpm(self, bpm):
		self.bpm = bpm
		self.tick_length = (60.0 / bpm) / (self.resolution / \
				float(self.meter[1]))


	def set_progression(self, progression):
		self.progression = progression

	def sync(self):
		# Execution time of current tick
		exec_time = time() - self.tick_start

		tick_length = self.block.get_tick_length(self.tick, \
				self.tick_length)

		if exec_time > tick_length:
			if self.verbose:
				print "Tick Overflow!"
			# Should tick be skipped?
		else:
			tick_length -= exec_time
		sleep(tick_length)


	def stop(self):
		for instr in self.instruments:
			instr.stop_playing_notes()
