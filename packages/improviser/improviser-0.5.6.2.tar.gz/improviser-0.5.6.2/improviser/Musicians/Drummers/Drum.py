from Instrument import Instrument
from mingus.containers.Note import Note

class Drum(Instrument):

	def __init__(self, params):
		params["channel"] = 9
		Instrument.__init__(self, params)

	def bass(self):
		return [Note("C", 2)]

	def crash(self):
		return [Note("C#", 3)]

	def hihat_closed(self):
		return [Note("G#", 2)]

	def hihat_opened(self):
		return [Note("A#", 2)]

	def ride(self):
		return [Note("B", 3)]

	def snare(self):
		return [Note("E", 2)]

