from BassInstrument import BassInstrument
from mingus.containers.Note import Note
from mingus.core import notes
from random import choice, random, randrange

class WalkingBass(BassInstrument):

	def generate_note(self, state):
		wild = 1.0
		if 'wild' in state:
			wild = state['wild']

		if state["tick"] % (state["resolution"] / 4.0) == 0 and \
				random() < 1.0 * wild:
			n = Note(choice(state["chord"]))
			while n > Note("E", 3):
				if n.octave >= 3:
					n.octave_down()
				else:
					break
			return [n]
		elif state["resolution"] > 4 and state["tick"] % \
			(state["resolution"] / 4.0) == \
			state["resolution"] / 8:
			
			n = Note(choice(state["chord"]))
			while n > Note("E", 3):
				if n.octave >= 3:
					n.octave_down()
				else:
					break
			if random() < 0.1 * wild:
				n.name = notes.diminish(n.name)
				return [n]
			else:
				return None
