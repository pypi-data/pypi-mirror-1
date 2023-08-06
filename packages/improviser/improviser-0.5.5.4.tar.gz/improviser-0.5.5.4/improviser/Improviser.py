#!/usr/bin/env python
from Sequencer import Sequencer
from Blocks import Block
from os import sys
from optparse import OptionParser
from mingus.core import notes

try:
	from mingus.extra import fluidsynth
except:
	print "Couldn't load the music library mingus."
	print "A download is available at http://mingus.googlecode.com/"
	sys.exit(1)

if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option("-b", "--bpm", dest="bpm", type="int",
		help="Set the bpm to start with.")
	parser.add_option("-f", "--frontend", dest="frontend", 
		metavar="F", help="Choose front-end [none, pygame]")
	parser.add_option("-k", "--key", dest="key",
		help="Set the key to start in.")
	parser.add_option("-q", "--quiet", action="store_false",
		dest="verbose")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=True)

	(options, args) = parser.parse_args()


	visual = None
	block = Block()

	if options.frontend == "pygame":
		from Visualizations import PygameBlockVisualization
		visual = PygameBlockVisualization(400,400)

	if options.key != None:
		if notes.is_valid_note(options.key):
			block.key = options.key
		else:
			if options.verbose:
				print "Invalid key:", options.key

	if options.bpm != None:
		block.bpm = options.bpm


	if not fluidsynth.init_fluidsynth():
		print "No running fluidsynth server found at port 9800."
		sys.exit(1)

	seq = Sequencer(block)
	seq.verbose = options.verbose
	if visual != None:
		seq.paint_function = visual.paint_screen
		seq.refresh_function = visual.refresh_screen
		seq.update_function = visual.update_screen
	seq.play()
