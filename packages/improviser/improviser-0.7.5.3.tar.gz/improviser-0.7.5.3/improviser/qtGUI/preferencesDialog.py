# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'improviser/qtGUI/preferences.ui'
#
# Created: Sat Jan 10 21:12:04 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_preferencesDialog(object):
    def setupUi(self, preferencesDialog):
        preferencesDialog.setObjectName("preferencesDialog")
        preferencesDialog.resize(392, 151)
        preferencesDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(preferencesDialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 100, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.soundfont = QtGui.QLineEdit(preferencesDialog)
        self.soundfont.setGeometry(QtCore.QRect(120, 30, 171, 23))
        self.soundfont.setObjectName("soundfont")
        self.label_9 = QtGui.QLabel(preferencesDialog)
        self.label_9.setGeometry(QtCore.QRect(20, 30, 81, 17))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtGui.QLabel(preferencesDialog)
        self.label_10.setGeometry(QtCore.QRect(20, 70, 81, 17))
        self.label_10.setObjectName("label_10")
        self.driver = QtGui.QComboBox(preferencesDialog)
        self.driver.setGeometry(QtCore.QRect(120, 70, 261, 22))
        self.driver.setObjectName("driver")
        self.pushButton = QtGui.QPushButton(preferencesDialog)
        self.pushButton.setGeometry(QtCore.QRect(300, 30, 80, 27))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(preferencesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), preferencesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), preferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(preferencesDialog)

    def retranslateUi(self, preferencesDialog):
        preferencesDialog.setWindowTitle(QtGui.QApplication.translate("preferencesDialog", "Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.soundfont.setStatusTip(QtGui.QApplication.translate("preferencesDialog", "The location of the soundfont to use", None, QtGui.QApplication.UnicodeUTF8))
        self.soundfont.setText(QtGui.QApplication.translate("preferencesDialog", "default.sf2", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setStatusTip(QtGui.QApplication.translate("preferencesDialog", "The location of the soundfont to use", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("preferencesDialog", "Soundfont", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("preferencesDialog", "Audio driver", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("preferencesDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))

