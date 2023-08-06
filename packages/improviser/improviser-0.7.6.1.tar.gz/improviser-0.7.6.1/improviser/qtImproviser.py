#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from qtGUI.qtUImain import Ui_MainWindow
from qtGUI.aboutDialog import Ui_aboutDialog
from qtGUI.instrumentDialog import Ui_instrumentDialog
from qtGUI.progressionDialog import Ui_progressionDialog
from qtGUI.blockDialog import Ui_blockDialog
from mingus.containers.Instrument import MidiInstrument
from mingus.core import chords
from mingus.core import progressions as mingus_progressions
from sys import argv
from os import path
import Musicians
import Progressions

import Options
from mingus.core import diatonic

APP_NAME = "qtImproviser"
APP_VERSION = "0.7"

class OptionClass:
	movement = "Movement"
	width=400
	height=400
	frontend="blocks"
	ensemble=None
	no_fluidsynth=False
	verbose=True
	meter = (4,4)

class InstrumentDialog(QtGui.QDialog):

	def __init__(self, item):
		QtGui.QDialog.__init__(self)
		self.item = item
		self.ui = Ui_instrumentDialog()
		self.ui.setupUi(self)
		self.setup()

	def setup(self):
		for x in Options.get_available_instruments():
			self.ui.algorithm.addItem(x)

		m = MidiInstrument()
		d = 1
		for x in m.names:
			self.ui.midi.addItem("%d. %s" % (d, x))
			d += 1

		self.connect(self.ui.algorithm, 
			QtCore.SIGNAL("activated(int)"),
			lambda x: self.load_instrument(self.ui.algorithm.currentText()))

		self.connect(self.ui.letring, 
			QtCore.SIGNAL("stateChanged(int)"),
			lambda x: self.ui.noteduration.setEnabled(x))

		self.connect(self.ui.buttonBox,
			QtCore.SIGNAL("accepted()"),
			lambda: self.save_instrument())

	def save_instrument(self):
		chan = self.ui.channel.value()
		drum = False
		if chan == 9:
			drum = True


		res = ""
		res += self.ui.algorithm.currentText() + " { "
		res += "channel:%d " % (self.ui.channel.value())
		if not drum:
			res += "midi_instr:%d " % (self.ui.midi.currentIndex())
		res += "start:%d " % self.ui.stepstart.value()
		res += "chance:%f " % (self.ui.chance.value())
		if self.ui.step.value() != 0:
			res += "step:%d " % self.ui.step.value()
		if self.ui.stepend.value() != -1:
			res += "end:%d " % self.ui.stepend.value()
		res += "max_velocity:%d min_velocity:%d " % (self.ui.maxvelocity.value(),
				self.ui.minvelocity.value())
		if self.ui.letring.isChecked():
			res += "let_ring:1 note_length:%d " % self.ui.noteduration.value()
		res += "}"
		self.item.setText(res)

	def load_instrument(self, instr_str):
		instr_str = str(instr_str)
		parts = instr_str.split(" ")

		index = combo_index_by_text(self.ui.algorithm, parts[0])
		if index > 0:
			self.ui.algorithm.setCurrentIndex(index)

		params = Options.parse_instrument_params(parts[1:])
		i = getattr(Musicians, parts[0])(params)
		self.ui.stepstart.setValue(i.start)
		self.ui.stepend.setValue(i.end)
		self.ui.step.setValue(i.step)
		if 'max_velocity' in i.params:
			self.ui.maxvelocity.setValue(i.params["max_velocity"])
		else:
			self.ui.maxvelocity.setValue(100)
		if 'min_velocity' in i.params:
			self.ui.minvelocity.setValue(i.params["min_velocity"])
		else:
			self.ui.minvelocity.setValue(50)

		if 'chance' in i.params:
			self.ui.chance.setValue(i.params['chance'])

		self.ui.channel.setEnabled(True)
		if 'channel' in i.params:
			self.ui.channel.setValue(i.params["channel"])
			if i.params["channel"] == 9:
				self.ui.channel.setEnabled(False)
		else:
			self.ui.channel.setValue(0)

		if 'let_ring' in i.params and i.params["let_ring"]:
			self.ui.letring.setChecked(True)
			self.ui.noteduration.setEnabled(True)
			if 'note_length' in i.params:
				self.ui.noteduration.setValue(i.params["note_length"])
			else:
				self.ui.noteduration.setValue(2)
		else:
			self.ui.letring.setChecked(False)
			self.ui.noteduration.setEnabled(False)

		if 'midi_instr' in i.params:
			self.ui.midi.setCurrentIndex(i.params['midi_instr'])
		else:
			self.ui.midi.setCurrentIndex(0)


def combo_index_by_text(combo, text):
	for x in range(combo.count()):
		if combo.itemText(x) == text:
			return x
	return -1


class ProgressionDialog(QtGui.QDialog):

	def __init__(self, item):
		QtGui.QDialog.__init__(self)
		self.item = item
		self.ui = Ui_progressionDialog()
		self.ui.setupUi(self)
		self.setup()

	def setup(self):
		self.ui.accidentals.addItem("")
		for x in range(1, 3):
			self.ui.accidentals.addItem("b" * x)
		for x in range(1, 3):
			self.ui.accidentals.addItem("#" * x)

		for x in ["I", "II", "III", "IV", "V", "VI", "VII"]:
			self.ui.romannumeral.addItem(x)

		for x in chords.chord_shorthand.keys():
			self.ui.chordsuffix.addItem(x)

		for x in ["0.25", "0.5", "0.75", "1", "2", "3", "4"]:
			self.ui.bars.addItem(x)
		self.ui.bars.setCurrentIndex(3)

		self.connect(self.ui.addchord,
			QtCore.SIGNAL("clicked()"),
			self.add_chord)

		self.connect(self.ui.addprogression,
			QtCore.SIGNAL("clicked()"),
			self.add_progression)

		self.connect(self.ui.updateprogression,
			QtCore.SIGNAL("clicked()"),
			lambda: self.add_progression(True))

		self.connect(self.ui.buttonBox,
			QtCore.SIGNAL("accepted()"),
			lambda: self.save_progression())

		self.connect(self.ui.clearsequence, 
			QtCore.SIGNAL("clicked()"),
			self.ui.progressionsequence.clear)

		self.connect(self.ui.removesequence,
			QtCore.SIGNAL("clicked()"),
			self.remove_sequence)

		self.connect(self.ui.upsequence,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progressionsequence))

		self.connect(self.ui.downsequence,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progressionsequence, False))

		self.connect(self.ui.progressionsequence,
			QtCore.SIGNAL("itemSelectionChanged()"),
			self.show_progression)

		self.connect(self.ui.updatechord,
			QtCore.SIGNAL("clicked()"),
			lambda: self.add_chord(True))

		self.connect(self.ui.clearprogression, 
			QtCore.SIGNAL("clicked()"),
			self.ui.progression.clear)

		self.connect(self.ui.removeprogression,
			QtCore.SIGNAL("clicked()"),
			self.remove_progression)

		self.connect(self.ui.upprogression,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progression))

		self.connect(self.ui.downprogression,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progression, False))

		self.connect(self.ui.progression,
			QtCore.SIGNAL("itemSelectionChanged()"),
			self.show_chord)


	def add_chord(self, update = False):
		if update:
			i = self.ui.progression.currentRow()
			if i == -1:
				return

		chord = str(self.ui.accidentals.currentText())
		chord += str(self.ui.romannumeral.currentText())
		chord += str(self.ui.chordsuffix.currentText())
		duration = str(self.ui.bars.currentText())
		r=  "%s %s" % (duration, chord)
		if not update:
			self.ui.progression.addItem(r)
		else:
			self.ui.progression.item(i).setText(r)

		self.ui.accidentals.setCurrentIndex(0)
		self.ui.romannumeral.setCurrentIndex(0)
		self.ui.chordsuffix.setCurrentIndex(0)
		self.ui.bars.setCurrentIndex(3)

	def add_progression(self, update = False):
		res=""

		if update:
			i = self.ui.progressionsequence.currentRow()
			if i == -1:
				return

		for x in range(self.ui.progression.count()):
			t = self.ui.progression.item(x).text()
			parts = t.split(" ")
			if parts[0] == "1":
				text = parts[1]
			else:
				text = "%s%s" % (parts[0], parts[1])
			res += "%s-" % text

		if res != "":
			r = str(self.ui.repeat.value() + 1) + " " + res[:-1]
			if not update:
				self.ui.progressionsequence.addItem(r)
			else:
				self.ui.progressionsequence.item(i).setText(r)

	def load_progression(self, prog_str):
		p = str(prog_str)
		parts = p.split(" ")
		if len(parts) == 0:
			return 

		if len(parts) == 1 and p in Options.get_available_progressions():
			x = Options.progression_to_string(getattr(Progressions, p))
			return self.load_progression("%s %s" % (p, x))

		self.ui.progressionname.setText(parts[0])
		if len(parts) > 3:
			params = parts[2:-1]
			for x in params:
				r = x.split("*")
				if len(r) == 2:
					self.ui.progressionsequence.addItem("%d %s" % (int(r[0]), r[1]))
				if len(r) == 1 and x != "":
					self.ui.progressionsequence.addItem("0 %s" % r[0])

	def save_progression(self):
		res = ""
		name = str(self.ui.progressionname.text()).replace(" ", "_")
		if name == "":
			return
		
		res += name + " { "
		for x in range(self.ui.progressionsequence.count()):
			t = self.ui.progressionsequence.item(x).text()
			parts = t.split(" ")
			res += "%d*%s " % (int(parts[0]), parts[1])
		res += " }"

		self.item.setText(res)


	def swap_list_item(self, lst, up = True):
		index = lst.currentRow()
		if index < 0:
			return
		c = lst.count()
		cur = lst.item(index)
		i1 = cur.text()
		if up:
			if index > 0:
				i2 = lst.item(index - 1)
				lst.setCurrentRow(index - 1)
			else:
				return 

		else:
			if index < c - 1:
				i2 = lst.item(index + 1)
				lst.setCurrentRow(index + 1)
			else:
				return
		t = i2.text()
		i2.setText(i1)
		cur.setText(t)

	def remove_sequence(self):
		i = self.ui.progressionsequence.currentRow()
		if i >= 0:
			self.ui.progressionsequence.takeItem(i)

	def remove_progression(self):
		i = self.ui.progression.currentRow()
		if i >= 0:
			self.ui.progression.takeItem(i)

	def show_progression(self):
		i = self.ui.progressionsequence.currentRow()
		if i >= 0:
			self.ui.progression.clear()
			prog = self.ui.progressionsequence.item(i).text()
			p = prog.split(" ")
			self.ui.repeat.setValue(int(p[0]) - 1)
			chords = p[1].split("-")
			for c in chords:
				if type(c[0]) != int:
					self.ui.progression.addItem("1 %s" % c)
				else:
					print "Can't parse bar length"

	def show_chord(self):
		i = self.ui.progression.currentRow()
		if i >= 0:
			parts = str(self.ui.progression.item(i).text()).split(" ")
			self.ui.bars.setCurrentIndex(combo_index_by_text(
				self.ui.bars, parts[0]))
			chord =mingus_progressions.parse_string(parts[1])
			self.ui.romannumeral.setCurrentIndex(combo_index_by_text(
				self.ui.romannumeral, chord[0]))
			self.ui.chordsuffix.setCurrentIndex(combo_index_by_text(
				self.ui.chordsuffix, chord[2]))

			acc = chord[1]
			r = ''
			while acc > 0:
				r += '#'
				acc -= 1
			while acc < 0:
				r += 'b'
				acc += 1
			self.ui.accidentals.setCurrentIndex(combo_index_by_text(
				self.ui.accidentals, r))







class BlockDialog(QtGui.QDialog):

	def __init__(self, item):
		QtGui.QDialog.__init__(self)
		self.item = item
		self.ui = Ui_blockDialog()
		self.ui.setupUi(self)
		self.setup()

	def setup(self):
		for x in ["From movement", 1, 2, 4, 8, 16, 32, 64, 128]:
			self.ui.resolution.addItem(str(x))
		for x in ["From movement"] + diatonic.basic_keys:
			self.ui.key.addItem(x)
		for x in Options.get_available_blocks():
			self.ui.blockcombo.addItem(x)

		self.connect(self.ui.buttonBox,
			QtCore.SIGNAL("accepted()"),
			lambda: self.save_block())

	def load_block(self, block_str):

		p = block_str.split(" ")
		self.ui.blockcombo.setCurrentIndex(combo_index_by_text(self.ui.blockcombo, p[0]))

		if len(p) == 1:
			return 

		params = Options.parse_block_params(p[1:])
		if 'duration' in params:
			self.ui.duration.setValue(params['duration'])
		if 'bpm' in params:
			self.ui.bpm.setValue(params["bpm"])
		if 'wild' in params:
			self.ui.wildness.setValue(params["wild"])
		if 'swing' in params:
			self.ui.swing.setChecked(True)
		if 'key' in params:
			self.ui.key.setCurrentIndex(combo_index_by_text(self.ui.key, params["key"]))
		if 'resolution' in params:
			self.ui.resolution.setCurrentIndex(combo_index_by_text(self.ui.resolution, str(params["resolution"])))



	def save_block(self):
	
		block = self.ui.blockcombo.currentText()
		res = str(block) + " { "

		bpm = self.ui.bpm.value()
		resolution = str(self.ui.resolution.currentText())
		key = str(self.ui.key.currentText())
		wild = self.ui.wildness.value()
		duration = self.ui.duration.value()
		swing = self.ui.swing.isChecked()

		if bpm != 0:
			res += "bpm:%d " % bpm
		if wild != 0.0:
			res += "wild:%f " % wild
		if duration != 0:
			res += "duration:%d " % duration
		
		if swing:
			res += "swing "
		if resolution != "From movement":
			res += "resolution:%s " % resolution
		if key != "From movement":
			res += "key:%s " % key

		
		
		res += "}"
		if res == str(block) + " { }":
			res = str(block)
		self.item.setText(res)

class ImproviserMainWindow(QtGui.QMainWindow):

	lastfile = ""
	lastmidi = ""


	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.fill_combos()
		self.connect_widgets()
		self.set_defaults()

	def set_title(self):
		p = "Untitled.imp"
		if self.lastfile != "":
			p = self.lastfile
		self.setWindowTitle("%s %s - %s" % (APP_NAME, APP_VERSION, p))


	def fill_combos(self):
		for x in Options.get_available_instruments():
			self.ui.instrumentcombo.addItem(x)
		for x in Options.get_available_blocks():
			self.ui.blockcombo.addItem(x)
		for x in Options.get_available_progressions():
			prog = Options.progression_to_string(getattr(Progressions, x))
			self.ui.progressioncombo.addItem("%s %s" % (x, prog))
		for x in Options.get_available_movements():
			self.ui.movement.addItem(x)
		for x in [1, 2, 4, 8, 16, 32, 64, 128]:
			self.ui.resolution.addItem(str(x))
		for x in diatonic.basic_keys:
			self.ui.key.addItem(x)
		for x in ['default', 'alsa', 'oss', 'jack', 'portaudio', 'coreaudio', 
				'sndmgr', 'Direct Sound']:
			self.ui.driver.addItem(x)
		for x in ['', 'cli', 'lines', 'blocks', 'mixed']:
			self.ui.visualization.addItem(x)
				

	def connect_widgets(self):
		self.connect(self.ui.startbutton, 
			QtCore.SIGNAL("clicked()"), 
			self.start_simulation)
		self.connect(self.ui.stopbutton, 
			QtCore.SIGNAL("clicked()"), 
			self.stop_simulation)
		self.connect(self.ui.addblockbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_block)
		self.connect(self.ui.addprogressionbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_progression)
		self.connect(self.ui.addinstrumentbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_instrument)
		self.connect(self.ui.upinstrument,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.instruments))
		self.connect(self.ui.downinstrument,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.instruments, False))
		self.connect(self.ui.removeblock,
			QtCore.SIGNAL("clicked()"),
			self.remove_block)
		self.connect(self.ui.clearblocks,
			QtCore.SIGNAL("clicked()"),
			self.ui.blocks.clear)
		self.connect(self.ui.upblock,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.blocks))
		self.connect(self.ui.downblock,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.blocks, False))
		self.connect(self.ui.removeinstrument,
			QtCore.SIGNAL("clicked()"),
			self.remove_instrument)
		self.connect(self.ui.clearinstruments,
			QtCore.SIGNAL("clicked()"),
			self.ui.instruments.clear)
		self.connect(self.ui.editblock,
			QtCore.SIGNAL("clicked()"),
			self.edit_block)
		self.connect(self.ui.editinstrument,
			QtCore.SIGNAL("clicked()"),
			self.edit_instrument)
		self.connect(self.ui.editprogression,
			QtCore.SIGNAL("clicked()"),
			self.edit_progression)
		self.connect(self.ui.removeprogression,
			QtCore.SIGNAL("clicked()"),
			self.remove_progression)
		self.connect(self.ui.upprogression,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progressions))
		self.connect(self.ui.downprogression,
			QtCore.SIGNAL("clicked()"),
			lambda: self.swap_list_item(self.ui.progressions, False))
		self.connect(self.ui.clearprogressions,
			QtCore.SIGNAL("clicked()"),
			self.ui.progressions.clear)
		self.connect(self.ui.action_About,
			QtCore.SIGNAL("activated()"),
			self.show_about)
		self.connect(self.ui.action_Load,
			QtCore.SIGNAL("activated()"),
			self.load_dialog)
		self.connect(self.ui.action_Save,
			QtCore.SIGNAL("activated()"),
			self.save_file)
		self.connect(self.ui.actionS_ave_as,
			QtCore.SIGNAL("activated()"),
			self.save_dialog)
		self.connect(self.ui.actionNew,
			QtCore.SIGNAL("activated()"),
			self.set_defaults)
		
	

	def set_defaults(self):

		self.lastfile = ""

		# Entries
		self.ui.projectname.setText("Untitled")
		self.ui.author.setText("")
		

		# Combo boxes
		self.ui.resolution.setCurrentIndex(3) # '8'
		self.ui.key.setCurrentIndex(6) # 'C'
		self.ui.movement.setCurrentIndex(0)
		self.ui.bpm.setValue(120)
		self.ui.wildness.setValue(0.5)
		self.ui.duration.setValue(1)
		self.ui.loop.setValue(1)

		# Lists
		self.ui.progressions.clear()
		self.ui.blocks.clear()
		self.ui.instruments.clear()

		# CheckBoxes
		self.ui.swing.setChecked(False)

		self.set_title()
	
	def add_block(self):
		self.ui.blocks.addItem(self.ui.blockcombo.currentText())

	def remove_block(self):
		i = self.ui.blocks.currentRow()
		if i >= 0:
			self.ui.blocks.takeItem(i)

	def add_progression(self):
		self.ui.progressions.addItem(
			self.ui.progressioncombo.currentText())

	def remove_progression(self):
		i = self.ui.progressions.currentRow()
		if i >= 0:
			self.ui.progressions.takeItem(i)

	def add_instrument(self):
		self.ui.instruments.addItem(
			self.ui.instrumentcombo.currentText())

	def remove_instrument(self):
		i = self.ui.instruments.currentRow()
		if i >= 0:
			self.ui.instruments.takeItem(i)

	def edit_block(self):
		cur = self.ui.blocks.item(self.ui.blocks.currentRow())
		if cur is None:
			return
		b = BlockDialog(self.ui.blocks.currentItem())
		b.load_block(str(cur.text()))
		b.show()
		b.exec_()

	def edit_instrument(self):
		cur = self.ui.instruments.item(self.ui.instruments.currentRow())
		if cur is None:
			return
		i = InstrumentDialog(self.ui.instruments.currentItem())
		i.load_instrument(str(cur.text()))
		i.show()
		i.exec_()

	def edit_progression(self):
		cur = self.ui.progressions.item(self.ui.progressions.currentRow())
		if cur is None:
			return
		p = ProgressionDialog(self.ui.progressions.currentItem())
		p.load_progression(cur.text())
		p.show()
		p.exec_()


	def get_file_name(self, name, n = 0):
		if n == 0:
			midi = name + ".mid"
		else:
			midi = name + str(n) + ".mid"
		if path.exists(midi):
			return self.get_file_name(name, n + 1)
		else:
			return midi

	def get_instruments(self):
		res = ""
		for x in range(self.ui.instruments.count()):
			res += str(self.ui.instruments.item(x).text()) + ","
		if res == "":
			return None
		return res[:-1]

	def get_progressions(self):
		res = ""
		for x in range(self.ui.progressions.count()):
			res += str(self.ui.progressions.item(x).text()) + ","
		return res[:-1]

	def get_blocks(self):
		res = ""
		for x in range(self.ui.blocks.count()):
			t = str(self.ui.blocks.item(x).text())
			res += t + ","
		return res[:-1]
	
	def show_about(self):
		w = QtGui.QDialog()
		i = Ui_aboutDialog()
		i.setupUi(w)
		w.show()
		w.activateWindow()
		w.exec_()

	def load_dialog(self):
		f = QtGui.QFileDialog()
		s = f.getOpenFileName(self, "Load improviser file.",
				"/home", "Improviser files (*.imp)")
		if s != "":
			try:
				o = Options.load_options_from_file(s, OptionClass())
				self.set_options(o)
				self.lastfile = s
				self.set_title()
			except Options.OptionError, err:
				self.set_status("Error: " + str(err))


	def save_file(self):
		if self.lastfile == "":
			self.save_dialog()
		else:
			try:
				Options.save_options(self.lastfile, 
					self.get_options())
			except IOError:
				self.set_status("Error: Couldn't open file for writing")

	def save_dialog(self):
		f = QtGui.QFileDialog()
		s = str(f.getSaveFileName(self, "Save improviser file.",
				"/home", "Improviser files (*.imp)"))
		if s != "":
			if s[-4:].lower() != ".imp":
				filename = s + ".imp"
			else:
				filename = s
			try:
				Options.save_options(filename, 
					self.get_options())
				self.lastfile = filename
				self.set_title()
			except IOError:
				self.set_status("Error: Couldn't open file for writing")

	def set_options(self, options):
		o = options

		# LineEdit
		self.ui.soundfont.setText(o.SF2)
		self.ui.projectname.setText(o.project)
		if hasattr(o, "author"):
			self.ui.author.setText(o.author)
		else:
			self.ui.author.setText('')


		# SpinBoxes
		self.ui.bpm.setValue(o.bpm)
		self.ui.duration.setValue(o.duration)
		self.ui.loop.setValue(o.loop)
		self.ui.wildness.setValue(o.wild)

		# ComboBoxes
		i = combo_index_by_text(self.ui.resolution, str(o.resolution))
		if i != -1:
			self.ui.resolution.setCurrentIndex(i)
		i = combo_index_by_text(self.ui.key, o.key)
		if i != -1:
			self.ui.key.setCurrentIndex(i)

		i = 0
		if hasattr(o, 'visualization'):
			i = combo_index_by_text(self.ui.visualization, o.visualization)
		self.ui.visualization.setCurrentIndex(i)


		# CheckBoxes
		self.ui.swing.setChecked(bool(o.swing))
		self.ui.no_fluidsynth.setChecked(bool(o.no_fluidsynth))

		# Lists
		self.ui.blocks.clear()
		self.ui.instruments.clear()
		self.ui.progressions.clear()

		if o.blocks != "":
			bloc = o.blocks.split(",")
			for b in bloc:
				parts = b.split(" ")
				block = parts[0]
				if block in Options.get_available_blocks():
					self.ui.blocks.addItem(b)
		if o.instrument != "":
			instr = o.instrument.split(",")
			for i in instr:
				parts =i.split(" ")
				if parts[0] in Options.get_available_instruments():
					self.ui.instruments.addItem(i)
		if o.progression != "":
			prog = o.progression.split(",")
			for p in prog:
				try:
					r = Options.parse_progression(p)
					self.ui.progressions.addItem(p)
				except:
					pass

	def get_options(self):
		o = OptionClass()

		# ComboBoxes
		o.resolution = int(str(self.ui.resolution.currentText()))
		o.key = str(self.ui.key.currentText())
		o.driver = str(self.ui.driver.currentText())
		o.frontend = str(self.ui.visualization.currentText())
		if o.frontend == '':
			o.frontend = None
		if o.driver == 'default':
			o.driver = None

		# SpinBoxes
		o.bpm = int(self.ui.bpm.value())
		o.duration = int(self.ui.duration.value())
		o.loop = int(self.ui.loop.value())
		o.wild = float(self.ui.wildness.value())

		# Checkboxes
		o.swing = int(self.ui.swing.isChecked())
		o.no_fluidsynth = int(self.ui.no_fluidsynth.isChecked())

		o.instrument = self.get_instruments()
		o.progression = self.get_progressions()
		o.blocks = self.get_blocks()

		# LineEdit
		o.SF2 = str(self.ui.soundfont.text())
		project = str(self.ui.projectname.text()).replace(" ", "_")
		if project == "":
			project = "Untitled"
		o.project = project
		o.author = str(self.ui.author.text())
		o.midifile = self.get_file_name(o.project)
		return o

	def swap_list_item(self, lst, up = True):
		index = lst.currentRow()
		if index < 0:
			return
		c = lst.count()
		cur = lst.item(index)
		i1 = cur.text()
		if up:
			if index > 0:
				i2 = lst.item(index - 1)
				lst.setCurrentRow(index - 1)
			else:
				return 

		else:
			if index < c - 1:
				i2 = lst.item(index + 1)
				lst.setCurrentRow(index + 1)
			else:
				return
		t = i2.text()
		i2.setText(i1)
		cur.setText(t)

				

	
	def set_status(self, msg):
		s = self.statusBar()
		s.showMessage(str(msg))

	def start_simulation(self):
		o = self.get_options()

		try:
			seq = Options.get_sequencer(o)
			self.ui.stopbutton.setEnabled(True)
			self.ui.startbutton.setEnabled(False)
			self.lastmidi = o.midifile

			self.seqthread  = SequencerThread(seq)
			self.connect(self.seqthread, QtCore.SIGNAL("finished()"), self.seqstopped)
			self.seqthread.start()


		except Options.OptionError, err:
			self.set_status("Error: " + str(err))

	def stop_simulation(self):
		self.ui.stopbutton.setEnabled(False)
		self.ui.startbutton.setEnabled(True)
		self.seqthread.seq.stop()
		self.seqthread.terminate()

	def seqstopped(self):
		self.ui.stopbutton.setEnabled(False)
		self.ui.startbutton.setEnabled(True)
		del self.seqthread


class SequencerThread(QtCore.QThread):
	def __init__(self, seq):
		self.seq = seq
		QtCore.QThread.__init__(self)

	def run(self):
		self.seq.play()


app = QtGui.QApplication(argv)
i = ImproviserMainWindow()
i.show()
app.exec_()
