from Drum import Drum
from random import random

class Snare(Drum):

	def generate_note(self, state):
		if random() < state["wild"]:
			return self.snare()
		else:
			return None
