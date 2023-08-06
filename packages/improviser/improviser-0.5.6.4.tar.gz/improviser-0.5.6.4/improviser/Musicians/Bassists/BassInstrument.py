from Instrument import Instrument
from mingus.containers.Note import Note
from mingus.core import notes
from random import choice, random

class BassInstrument(Instrument):

	def generate_note(self, state):
		wild = 1.0
		if 'wild' in state:
			wild = state['wild']

		if state["tick"] % (state["resolution"] / 4.0) == 0 and \
				random() < 1.0 * wild:
			n = Note(choice(state["chord"]))
			n.octave_down()
			return [n]
		elif state["tick"] % (state["resolution"] / 4.0) == \
				state["resolution"] / 8 and \
				random() < 0.2 * wild:
			
			n = Note(choice(state["chord"]))
			n.octave_down()
			n.name = notes.diminish(n.name)
			return [n]
