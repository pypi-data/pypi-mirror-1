#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from qtUImain import Ui_MainWindow
from sys import argv

import Options
from mingus.core import diatonic

class OptionClass:
	movement = "Movement"
	blocks="Block"
	width=400
	height=400
	frontend="DefaultVisualization"
	ensemble="none"
	no_fluidsynth=False
	instrument="RockDrum"
	progression="reincarnatie"
	verbose=True
	midifile="default.mid"
	meter = (4,4)
	pass

class ImproviserMainWindow(QtGui.QMainWindow):

	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.fill_combos()
		self.connect_widgets()
		self.set_defaults()

	def fill_combos(self):
		for x in Options.get_available_instruments():
			self.ui.instrumentcombo.addItem(x)
		for x in Options.get_available_blocks():
			self.ui.blockcombo.addItem(x)
		for x in Options.get_available_progressions():
			self.ui.progressioncombo.addItem(x)
		for x in Options.get_available_movements():
			self.ui.movement.addItem(x)
		for x in [1, 2, 4, 8, 16, 32, 64, 128]:
			self.ui.resolution.addItem(str(x))
		for x in diatonic.basic_keys:
			self.ui.key.addItem(x)

	def connect_widgets(self):
		self.connect(self.ui.startbutton, QtCore.SIGNAL("clicked()"), self.start_simulation)

	def set_defaults(self):
		self.ui.resolution.setCurrentIndex(3)
		self.ui.key.setCurrentIndex(6)

	def start_simulation(self):
		o = OptionClass()
		o.SF2 = str(self.ui.soundfont.text())
		o.resolution = int(str(self.ui.resolution.currentText()))
		o.key = str(self.ui.key.currentText())
		o.bpm = int(self.ui.bpm.value())
		o.duration = int(self.ui.duration.value())
		o.loop = int(self.ui.loop.value())
		o.wild = float(self.ui.wildness.value())
		o.swing = self.ui.swing.checkState()
		seq = Options.get_sequencer(o)
		seq.play()


app = QtGui.QApplication(argv)
i = ImproviserMainWindow()
i.show()
app.exec_()
