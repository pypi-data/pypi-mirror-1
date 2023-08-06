from Drum import Drum
from random import random

class JazzDrum(Drum):

	using_ride = False

	def generate_note(self, state):
		n = []
		if 'chance' in self.params:
			chance = self.params["chance"]
		else:
			chance = 0.9
		if 'wild' in state:
			wild = state["wild"]
		else:
			wild = 1.0

		if self.using_ride:
			if state["tick"] % 2 == 0 and random() < chance:
				n += self.ride()
		else:
			if state["tick"] % 2 == 0:
				if random() < chance * 0.4 * wild:
					n += self.hihat_closed()
				elif random() < chance * 0.4 * wild:
					n += self.hihat_opened()

		snare_scalar = 0.5
		if state["meter"][0] in [4, 8]:
			snare_scalar = 0.5
		elif state["meter"][0] in [3, 6]:
			snare_scalar = 0.66

		if state["iteration_tick"] == 0 and \
				random() < chance * 0.2 * wild:
			n += self.crash()
			n += self.bass()


		elif state["tick"] == int(round(state["ticks"] * snare_scalar))\
				and random() < chance * 0.75 * wild:
					n += self.snare()

		elif random() <  0.075 * wild:
			n += self.snare()
		elif random() < chance * 0.15 * wild:
			n += self.bass()


		if random() < chance * 0.05 * wild:
			self.using_ride = not(self.using_ride)

		return n
