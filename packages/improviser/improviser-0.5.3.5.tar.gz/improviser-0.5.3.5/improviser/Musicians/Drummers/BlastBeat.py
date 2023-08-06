from Drum import Drum
from mingus.containers.NoteContainer import NoteContainer

class BlastBeat(Drum):

	def generate_note(self, state):

		n = []
		if state["tick"] % 2 == 0:
			n += self.bass()
			if state["iteration_tick"] == 0:
				n += self.crash()
			else:
				n += self.hihat_closed()
		else:
			n = self.snare()
		return NoteContainer(n)

