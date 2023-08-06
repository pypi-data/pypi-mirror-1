#!/usr/bin/env python
from Sequencer import Sequencer
import Blocks
from Blocks import Block
from os import sys
from optparse import OptionParser
from mingus.core import notes
import Bands
import Progressions
import Musicians
from Instrument import Instrument

try:
	from mingus.midi import fluidsynth
except:
	print "Couldn't load the music library mingus."
	print "A download is available at http://mingus.googlecode.com/"
	sys.exit(1)

def get_available_bands():
	return [x for x in Bands.__dict__ if \
		type(getattr(Bands, x)) == type([])]

def get_available_progressions():
	return [x for x in Progressions.__dict__ if \
		type(getattr(Progressions, x)) == type([]) and \
		x[0] != "_"]

def get_available_instruments():
	return [x for x in Bands.__dict__ if type(getattr(Bands, x)) == \
		type(Instrument) and issubclass(getattr(Bands,x), Instrument)]


def get_available_blocks():
	return [x for x in Blocks.__dict__ if type(getattr(Blocks, x)) == \
		type(Block) and issubclass(getattr(Blocks,x), Block)]

def check_options(test, test_func, test_str, module, dest):

	if test != None:
		if test in test_func():
			dest = getattr(module, test)
			return dest
		else:
			print "Unknown %s:" % test_str, test
			return False
	return False

if __name__ == '__main__':

	parser = OptionParser()
	parser.add_option("-b", "--bpm", dest="bpm", type="int",
		help="Set the bpm to start with.")
	parser.add_option("--block", dest="block", help="Set the block to start with.")
	parser.add_option("-d", "--duration", dest="duration", type="int",
		help="Set the number of times the progression should be repeated.")
	parser.add_option("-e", "--ensemble", dest="ensemble", 
		metavar="EN", help="Set the ensemble")
	parser.add_option("-f", "--frontend", dest="frontend", 
		metavar="F", help="Choose front-end [blocks, lines, mixed]")
	parser.add_option("--height", dest='height', type='int',
		default=400, help='Height of the visualization screen')
	parser.add_option("-i", "--instrument", help="Specify instruments. Separate by comma.", dest="instrument")
	parser.add_option("-l", "--list", dest="list", 
		help="List [blocks, ensembles, progressions, instruments]. Don't play.")
	parser.add_option("-k", "--key", dest="key",
		help="Set the key to start in.")
	parser.add_option("-n", "--no-fluidsynth", dest="no_fluidsynth",
		action="store_true", default=False, help="Don't connect to a fluidsynth server, just write the midi file."),
	parser.add_option("-o", "--output-file", dest="midifile", 
		help="The file to write the midi to.", default="improviser.mid"),
	parser.add_option("-p", "--progression", dest="progression",
		help="Set the progression.")
	parser.add_option("-r", "--resolution", dest="resolution",
		default=8, type="int",
		help="The resolution [1,2,4,8,16,32,etc]")
	parser.add_option("-q", "--quiet", action="store_false",
		dest="verbose", default=True, 
		help="Don't output to stdout")
	parser.add_option("-s", "--swing", action="store_true",
		dest="swing", default=False, help="Set swing")
	parser.add_option("--sf2", dest="SF2", default="soundfont.sf2", help="The soundfont to load.")
	parser.add_option("-w", "--wildness", type="float", dest="wild",
		help="Floating point number indicating wildness")
	parser.add_option("--width", dest="width", default=400,
		type="int", help="Width of the visualization screen")

	(options, args) = parser.parse_args()


	visual = None
	b = check_options(options.block, get_available_blocks, 
			"block", Blocks, visual)
	if b != False:
		block = b()
	else:
		block = Block()
	block.swing = options.swing
	block.resolution = options.resolution
	w = options.width
	h = options.height

	if options.frontend == "blocks":
		from Visualizations import PygameBlockVisualization
		visual = PygameBlockVisualization(w,h)
	elif options.frontend == "lines":
		from Visualizations import PygameLineVisualization
		visual = PygameLineVisualization(w,h)
	elif options.frontend == "mixed":
		from Visualizations import PygameMixedVisualizations
		visual = PygameMixedVisualizations(w,h)

	if options.list != None:
		if options.list == "ensembles" or \
			options.list[0] == 'e':
			i = 1
			for x in get_available_bands():
				print "%d. %s" % (i, x)
				i += 1
		elif options.list == "progressions" or\
			options.list[0] == 'p':
			i = 1
			for x in get_available_progressions():
				print "%d. %s" % (i, x)
				i += 1
		elif options.list == "instruments" or\
			options.list[0] == 'i':
			i = 1
			for x in get_available_instruments():
				print "%d. %s" % (i, x)
				i += 1
		elif options.list == "blocks" or\
			options.list[0] == 'b':
			i = 1
			for x in get_available_blocks():
				print "%d. %s" % (i, x)
				i += 1
		else:
			print "Unknown list", options.list
		sys.exit(0)

	b = check_options(options.ensemble, get_available_bands, 
			"ensemble", Bands, block.instruments)
	if b != False:
		block.instruments = b

	b = check_options(options.progression, get_available_progressions,
			"progression", Progressions, block.progressions)
	if b != False:
		block.progressions = b



	if options.instrument != None:
		for inst in options.instrument.split(","):
			c =0 
			if inst in get_available_instruments():
				i = getattr(Musicians, inst)
				i = i({'channel': c, 'start': 0})
				c += 1
				block.instruments += [i]
			else:
				if options.verbose:
					print "Unknown instrument:", inst

	if options.key != None:
		if notes.is_valid_note(options.key):
			block.key = options.key
		else:
			if options.verbose:
				print "Invalid key:", options.key

	if options.bpm != None:
		block.bpm = options.bpm

	if options.duration != None:
		block.duration = options.duration

	if options.wild != None:
		block.wildness = options.wild

	if not options.no_fluidsynth:
		if not fluidsynth.init(options.SF2):
			print "Couldn't load '%s', quiting. Use the --sf2 option to set the soundfont." % options.SF2
			sys.exit(1)
		fluidsynth.stop_everything()

	if block.instruments == []:
		print "No instruments or ensemble selected."

	for x in block.instruments:
		x.no_fluidsynth = options.no_fluidsynth

	seq = Sequencer(block)
	seq.verbose = options.verbose
	seq.no_fluidsynth = options.no_fluidsynth
	seq.output_file = options.midifile
	if visual != None:
		seq.paint_function = visual.paint_screen
		seq.refresh_function = visual.refresh_screen
		seq.update_function = visual.update_screen
	seq.play()
