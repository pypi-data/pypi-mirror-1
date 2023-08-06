#!/usr/bin/env python
from Sequencer import Sequencer
from Blocks import Block
from os import sys
try:
	from mingus.extra import fluidsynth
except:
	print "Couldn't load the music library mingus."
	print "A download is available at http://mingus.googlecode.com/"
	sys.exit(1)

if __name__ == '__main__':

	if not fluidsynth.init_fluidsynth():
		print "No running fluidsynth server found at port 9800."
		sys.exit(1)

	seq = Sequencer(Block())
	seq.play()
