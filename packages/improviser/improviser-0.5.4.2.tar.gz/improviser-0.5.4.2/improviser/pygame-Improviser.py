#!/usr/bin/env python
from Sequencer import Sequencer
from Blocks import Block
from mingus.extra import fluidsynth
from os import sys
from Visualizations import *


WIDTH = 300
HEIGHT = 300

if __name__ == '__main__':

	if not fluidsynth.init_fluidsynth():
		print "No running fluidsynth server found at port 9800."
		sys.exit(1)

	visual = PygameBlockVisualization(400,400)

	seq = Sequencer(Block())
	seq.paint_function = visual.paint_screen
	seq.refresh_function = visual.refresh_screen
	seq.update_function = visual.update_screen
	seq.play()
