from PyQt4 import QtCore, QtGui
from qtGUI.preferencesDialog import Ui_preferencesDialog

class PreferencesDialog(QtGui.QDialog):

	def __init__(self, show_main):
		QtGui.QDialog.__init__(self)
		self.show_main = show_main
		self.ui = Ui_preferencesDialog()
		self.ui.setupUi(self)
		self.setup()

	def setup(self):
		for x in ['default', 'alsa', 'oss', 'jack', 'portaudio', 'coreaudio', 
				'sndmgr', 'Direct Sound']:
			self.ui.driver.addItem(x)

		self.connect(self.ui.buttonBox,
			QtCore.SIGNAL("accepted()"),
			self.open_window)

		self.connect(self.ui.browsebutton,
			QtCore.SIGNAL("clicked()"),
			self.load_dialog)

		self.connect(self.ui.no_fluidsynth,
			QtCore.SIGNAL("stateChanged(int)"),
			lambda x: self.ui.browsebutton.setEnabled(not(x)) or \
					self.ui.driver.setEnabled(not(x)))

	def toggle_enabled(self):
		if self.ui.no_fluidsynth.isChecked():
			self.ui.browsebutton.enabled()
		else:
			self.ui.browsebutton.enabled()



	def open_window(self):
		soundfont = str(self.ui.soundfont.text())
		driver = str(self.ui.driver.currentText())
		no_fluidsynth = int(self.ui.no_fluidsynth.isChecked())

		if no_fluidsynth:
			self.show_main()
			self.reject()
		else:
			if soundfont != "":
				self.show_main(False, soundfont, driver)
				self.reject()

	def load_dialog(self):
		f = QtGui.QFileDialog()
		s = f.getOpenFileName(self, "Load soundfont.",
				"/home", "Soundfont (*.sf2)")
		if s != "":
			self.ui.soundfont.setText(s)


