from PyQt4 import QtCore, QtGui
from qtUImain import Ui_MainWindow
from aboutDialog import Ui_aboutDialog
from ProgressionDialog import ProgressionDialog
from InstrumentDialog import InstrumentDialog
from BlockDialog import BlockDialog
from os import path, environ
from mingus.core import diatonic
import Progressions
import Options

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
		for x in Options.get_available_progressions():
			prog = Options.progression_to_string(getattr(Progressions, x))
			self.ui.progressioncombo.addItem("%s %s" % (x, prog))
		for x in Options.get_available_movements():
			self.ui.movement.addItem(x)
		for x in [1, 2, 4, 8, 16, 32, 64, 128]:
			self.ui.resolution.addItem(str(x))
		for x in diatonic.basic_keys:
			self.ui.key.addItem(x)
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
			lambda: self.ui.progressions.clear() or self.progression_changed())
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
		self.connect(self.ui.instrumentcombo,
			QtCore.SIGNAL("activated(int)"),
			lambda x: self.add_instrument())
		self.connect(self.ui.progressioncombo, 
			QtCore.SIGNAL("activated(int)"),
			lambda x: self.add_progression())
		self.connect(self.ui.bpmslide,
			QtCore.SIGNAL("sliderMoved(int)"),
			lambda x: self.ui.bpm.setValue(x * 10))
		self.connect(self.ui.bpm,
			QtCore.SIGNAL("valueChanged(int)"),
			lambda x: self.ui.bpmslide.setValue(x / 10))
		self.connect(self.ui.loopslide,
			QtCore.SIGNAL("sliderMoved(int)"),
			lambda x: self.ui.loop.setValue(x * 10))
		self.connect(self.ui.loop,
			QtCore.SIGNAL("valueChanged(int)"),
			lambda x: self.ui.loopslide.setValue(x / 10))
		self.connect(self.ui.wildslide,
			QtCore.SIGNAL("sliderMoved(int)"),
			lambda x: self.ui.wildness.setValue(x / 10.0))
		self.connect(self.ui.wildness,
			QtCore.SIGNAL("valueChanged(double)"),
			lambda x: self.ui.wildslide.setValue(int(x * 10)))
		self.connect(self.ui.copyblock,
			QtCore.SIGNAL("clicked()"),
			self.copy_block)
		self.connect(self.ui.copyinstrument,
			QtCore.SIGNAL("clicked()"),
			self.copy_instrument)
		self.connect(self.ui.copyprogression,
			QtCore.SIGNAL("clicked()"),
			self.copy_progression)
		self.connect(self.ui.exportprogressions,
			QtCore.SIGNAL("clicked()"),
			self.export_progression)
		self.connect(self.ui.importprogression,
			QtCore.SIGNAL("clicked()"),
			self.import_progression)
		


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

		# Slides
		self.ui.bpmslide.setValue(12)
		self.ui.loopslide.setValue(1)
		self.ui.wildslide.setValue(5)

		# Lists
		self.ui.progressions.clear()
		self.ui.blocks.clear()
		self.ui.instruments.clear()

		# CheckBoxes
		self.ui.swing.setChecked(False)

		self.set_title()
		self.progression_changed()
	
	def add_block(self):
		self.ui.blocks.addItem("Block")
		self.ui.blocks.setCurrentRow(int(self.ui.blocks.count()) - 1)
		self.edit_block()

	def remove_block(self):
		i = self.ui.blocks.currentRow()
		if i >= 0:
			self.ui.blocks.takeItem(i)

	def copy_block(self):
		i = self.ui.blocks.currentRow()
		if i >= 0:
			self.ui.blocks.addItem(self.ui.blocks.item(i).text())

	def add_progression(self):
		self.ui.progressions.addItem(
			self.ui.progressioncombo.currentText())
		self.ui.progressions.setCurrentRow(int(self.ui.progressions.count()) - 1)
		self.edit_progression()
		self.progression_changed()

	def remove_progression(self):
		i = self.ui.progressions.currentRow()
		if i >= 0:
			self.ui.progressions.takeItem(i)
		self.progression_changed()

	def copy_progression(self):
		i = self.ui.progressions.currentRow()
		if i >= 0:
			self.ui.progressions.addItem(self.ui.progressions.item(i).text())
		self.progression_changed()

	def import_progression(self):
		h = "/home"
		if 'HOME' in environ:
			h = environ["HOME"]
		f = QtGui.QFileDialog()
		s = f.getOpenFileName(self, "Load progressions.",
				h, "Progressions (*.prg)")
		if s != "":
			try:
				fp = open(s, "r")
				for x in fp.readlines():
					prog = x.split(",")
					for p in prog:
						try:
							r = Options.parse_progression(p)
							self.ui.progressions.addItem(p)
						except:
							pass
				fp.close()
			except Options.OptionError, err:
				self.set_status("Error: " + str(err))
		self.progression_changed()


	def export_progression(self):
		h = "/home"
		if 'HOME' in environ:
			h = environ["HOME"]
		prog = self.get_progressions()
		if prog == "":
			return 
		
		f = QtGui.QFileDialog()
		s = str(f.getSaveFileName(self, "Save progressions.",
				h, "Progressions (*.prg)"))
		if s != "":
			if s[-4:].lower() != ".prg":
				filename = s + ".prg"
			else:
				filename = s
			try:
				fp = open(filename, "w")
				fp.write(prog)
				fp.close()
			except IOError:
				self.set_status("Error: Couldn't open file for writing")
		self.progression_changed()

	def progression_changed(self):
		if self.ui.progressions.count() == 0:
			self.enable_progression(False)
		else:
			self.enable_progression(True)
		

	def enable_progression(self, enable = True):
		self.ui.exportprogressions.setEnabled(enable)
		self.ui.upprogression.setEnabled(False)
		self.ui.downprogression.setEnabled(False)
		self.ui.clearprogressions.setEnabled(enable)
		self.ui.copyprogression.setEnabled(enable)
		self.ui.editprogression.setEnabled(enable)
		self.ui.removeprogression.setEnabled(enable)

		if enable and self.ui.progressions.count() > 1:
			self.ui.upprogression.setEnabled(enable)
			self.ui.downprogression.setEnabled(enable)

	def add_instrument(self):
		self.ui.instruments.addItem(self.ui.instrumentcombo.currentText())
		self.ui.instruments.setCurrentRow(int(self.ui.instruments.count()) -1)
		self.edit_instrument()

	def remove_instrument(self):
		i = self.ui.instruments.currentRow()
		if i >= 0:
			self.ui.instruments.takeItem(i)

	def copy_instrument(self):
		i = self.ui.instruments.currentRow()
		if i >= 0:
			self.ui.instruments.addItem(self.ui.instruments.item(i).text())


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
		h = "/home"
		if 'HOME' in environ:
			h = environ["HOME"]
		f = QtGui.QFileDialog()
		s = f.getOpenFileName(self, "Load improviser file.",
				h, "Improviser files (*.imp)")
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
		h = "/home"
		if 'HOME' in environ:
			h = environ["HOME"]
		f = QtGui.QFileDialog()
		s = str(f.getSaveFileName(self, "Save improviser file.",
				h, "Improviser files (*.imp)"))
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
		self.ui.projectname.setText(o.project.replace("_", " "))
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
		if hasattr(o, "movement"):
			i = combo_index_by_text(self.ui.movement, str(o.movement))
		self.ui.movement.setCurrentIndex(i)

		i = 0
		if hasattr(o, 'visualization'):
			i = combo_index_by_text(self.ui.visualization, o.visualization)
		self.ui.visualization.setCurrentIndex(i)


		# CheckBoxes
		self.ui.swing.setChecked(bool(o.swing))

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
		o.driver = self.driver
		o.SF2 = self.soundfont
		o.frontend = str(self.ui.visualization.currentText())
		o.movement = str(self.ui.movement.currentText())
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
		o.no_fluidsynth = int(self.no_fluidsynth)

		o.instrument = self.get_instruments()
		o.progression = self.get_progressions()
		o.blocks = self.get_blocks()

		# LineEdit
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
			q = QtGui.QMessageBox.warning(self, "Error", str(err), 1, 0)

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


def combo_index_by_text(combo, text):
	for x in range(combo.count()):
		if combo.itemText(x) == text:
			return x
	return -1

