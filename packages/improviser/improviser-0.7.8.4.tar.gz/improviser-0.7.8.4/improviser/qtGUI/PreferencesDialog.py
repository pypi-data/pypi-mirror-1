from PyQt4 import QtCore, QtGui
from qtGUI.preferencesDialog import Ui_preferencesDialog
from os import environ, path
import urllib
import md5

class PreferencesDialog(QtGui.QDialog):

	def __init__(self, show_main):
		QtGui.QDialog.__init__(self)
		self.show_main = show_main
		self.ui = Ui_preferencesDialog()
		self.ui.setupUi(self)
		self.setup()
		self.try_load_from_file()

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

	def try_load_from_file(self):
		if "HOME" in environ:
			f = path.join(environ["HOME"], ".improviser")
			if path.exists(f):
				try:
					fp = open(f, "r")
					for x in fp.readlines():
						option = x[:-1]
						parts = option.split(":")
						key = parts[0]
						if key == "soundfont":
							self.ui.soundfont.setText(":".join(parts[1:]))
						elif key == "driver":
							i = combo_index_by_text(self.ui.driver, "".join(parts[1:]))
							self.ui.driver.setCurrentIndex(int(i))
						elif key == "no_fluidsynth":
							if parts[1] == "1":
								self.ui.browsebutton.setEnabled(False)
								self.ui.driver.setEnabled(False)
								self.ui.no_fluidsynth.setChecked(True)
						elif key == "user":
							self.ui.username.setText(":".join(parts[1:]))
						elif key == "pass":
							self.ui.password.setText(":".join(parts[1:]))
					fp.close()
				except:
					pass

	def try_save_file(self):
		if "HOME" in environ:
			f = path.join(environ["HOME"], ".improviser")
			try:
				fp = open(f, "w")
				fp.write("soundfont:%s\n" % self.ui.soundfont.text())
				fp.write("driver:%s\n" % self.ui.driver.currentText())
				fp.write("no_fluidsynth:%d\n" % self.ui.no_fluidsynth.isChecked())
				fp.write("user:%s\n" % self.ui.username.text())
				fp.write("pass:%s\n" % self.ui.password.text())
				fp.close()
			except:
				pass


	def login(self):
		return True
		params = urllib.urlencode({"name": str(self.ui.username.text()),
			"pass": md5.new(str(self.ui.password.text())).digest()})
		try:
			f = urllib.urlopen("http://localhost/improviser/login.php?%s" % params)
		except:
			return False
		res = f.read()
		f.close()
		if res == "OK":
			return True
		return False


	def toggle_enabled(self):
		if self.ui.no_fluidsynth.isChecked():
			self.ui.browsebutton.enabled()
		else:
			self.ui.browsebutton.enabled()



	def open_window(self):
		soundfont = str(self.ui.soundfont.text())
		driver = str(self.ui.driver.currentText())
		no_fluidsynth = int(self.ui.no_fluidsynth.isChecked())
		self.try_save_file()

		params = { "username": str(self.ui.username.text()),
			   "password": str(self.ui.password.text()),
			   "login": self.login() }

		if no_fluidsynth:
			self.show_main(params)
			self.reject()
		else:
			if soundfont != "":
				params["soundfont"] = soundfont
				params["driver"] = driver
				self.show_main(params)
				self.reject()

	def load_dialog(self):
		h = "/home"
		if 'HOME' in environ:
			h = environ["HOME"]
		f = QtGui.QFileDialog()
		s = f.getOpenFileName(self, "Load soundfont.",
				h, "Soundfont (*.sf2)")
		if s != "":
			self.ui.soundfont.setText(s)


def combo_index_by_text(combo, text):
	for x in range(combo.count()):
		if combo.itemText(x) == text:
			return x
	return -1
