#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from qtGUI.MainWindow import ImproviserMainWindow
from qtGUI.PreferencesDialog import PreferencesDialog
from sys import argv

def show_main(params):
	i = ImproviserMainWindow()
	if 'soundfont' not in params:
		i.no_fluidsynth = True
		i.soundfont = ''
		i.driver = ''
	else:
		i.no_fluidsynth = False
		i.soundfont = params["soundfont"]
		i.driver = params["driver"]
	i.show()

app = QtGui.QApplication(argv)
p = PreferencesDialog(show_main)
p.show()
app.exec_()


