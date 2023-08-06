#!/usr/bin/env python
from Sequencer import Sequencer
from Blocks import Block
from mingus.extra import fluidsynth
from os import sys


class Improviser:

	options = {}

	def __init__(self):
		self.seq = Sequencer(Block())

	def play(self):
		self.seq.play()


if __name__ == '__main__':

	if not fluidsynth.init_fluidsynth():
		print "No running fluidsynth server found at port 9800."
		sys.exit(1)

	seq = Sequencer(Block())
	seq.play()
