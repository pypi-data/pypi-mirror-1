#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from qtGUI.qtUImain import Ui_MainWindow
from qtGUI.aboutDialog import Ui_aboutDialog
from sys import argv
from os import path

import Options
from mingus.core import diatonic

class OptionClass:
	movement = "Movement"
	width=400
	height=400
	frontend="DefaultVisualization"
	ensemble="none"
	no_fluidsynth=False
	verbose=True
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
		self.connect(self.ui.startbutton, 
			QtCore.SIGNAL("clicked()"), 
			self.start_simulation)
		self.connect(self.ui.addblockbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_block)
		self.connect(self.ui.addprogressionbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_progression)
		self.connect(self.ui.addinstrumentbutton,
			QtCore.SIGNAL("clicked()"),
			self.add_instrument)
		self.connect(self.ui.removeblock,
			QtCore.SIGNAL("clicked()"),
			self.remove_block)
		self.connect(self.ui.removeinstrument,
			QtCore.SIGNAL("clicked()"),
			self.remove_instrument)
		self.connect(self.ui.removeprogression,
			QtCore.SIGNAL("clicked()"),
			self.remove_progression)
		self.connect(self.ui.action_About,
			QtCore.SIGNAL("activated()"),
			self.show_about)

	def set_defaults(self):
		self.ui.resolution.setCurrentIndex(3) # '8'
		self.ui.key.setCurrentIndex(6) # 'C'
	
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
			res += str(self.ui.blocks.item(x).text()) + ","
		return res[:-1]
	
	def show_about(self):
		w = QtGui.QDialog()
		i = Ui_aboutDialog()
		i.setupUi(w)
		w.show()
		w.activateWindow()
		w.exec_()

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
		o.no_fluidsynth = self.ui.no_fluidsynth.checkState()
		o.instrument = self.get_instruments()
		o.progression = self.get_progressions()
		o.blocks = self.get_blocks()
		project = str(self.ui.projectname.text())
		if project == "":
			project = "Untitled"
		o.midifile = self.get_file_name(project)


		try:
			seq = Options.get_sequencer(o)
			self.ui.stopbutton.setEnabled(True)
			self.ui.startbutton.setEnabled(False)
			seq.play()
		except Options.OptionError, err:
			print err

		self.ui.startbutton.setEnabled(True)
		self.ui.stopbutton.setEnabled(False)

app = QtGui.QApplication(argv)
i = ImproviserMainWindow()
i.show()
app.exec_()
