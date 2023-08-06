from Instrument import Instrument
from mingus.containers.Note import Note
from mingus.core import notes
from random import choice, random

class ChromaticSoloist(Instrument):

	last_note = ''
	up = True

	def generate_note(self, state):
		if self.last_note == '':
			n = choice(state["chord"])
		else:
			if self.up:
				n = notes.augment(self.last_note)
			else:
				n = notes.diminish(self.last_note)
			

		self.last_note = n
		if random() < 0.20:
			self.up = not(self.up)

		if random() > 0.6:
			return [Note(n)]
		elif random() > 0.8 and state["tick"] % 2 == 0:
			return [Note(choice(state["chord"]))]
		else:
			return None
