# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'improviser/qtGUI/block.ui'
#
# Created: Wed Jan 14 09:35:01 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_blockDialog(object):
    def setupUi(self, blockDialog):
        blockDialog.setObjectName("blockDialog")
        blockDialog.resize(549, 202)
        blockDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(blockDialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtGui.QGroupBox(blockDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 521, 141))
        self.groupBox.setObjectName("groupBox")
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(270, 30, 111, 17))
        self.label_5.setObjectName("label_5")
        self.bpm = QtGui.QSpinBox(self.groupBox)
        self.bpm.setGeometry(QtCore.QRect(150, 30, 111, 23))
        self.bpm.setMinimum(1)
        self.bpm.setMaximum(1000)
        self.bpm.setProperty("value", QtCore.QVariant(120))
        self.bpm.setObjectName("bpm")
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(30, 30, 111, 17))
        self.label_6.setObjectName("label_6")
        self.wildness = QtGui.QDoubleSpinBox(self.groupBox)
        self.wildness.setGeometry(QtCore.QRect(150, 70, 111, 23))
        self.wildness.setDecimals(5)
        self.wildness.setMaximum(100.0)
        self.wildness.setSingleStep(0.025)
        self.wildness.setProperty("value", QtCore.QVariant(0.5))
        self.wildness.setObjectName("wildness")
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(30, 70, 111, 17))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setGeometry(QtCore.QRect(270, 70, 101, 17))
        self.label_8.setObjectName("label_8")
        self.resolution = QtGui.QComboBox(self.groupBox)
        self.resolution.setGeometry(QtCore.QRect(390, 30, 111, 22))
        self.resolution.setObjectName("resolution")
        self.key = QtGui.QComboBox(self.groupBox)
        self.key.setGeometry(QtCore.QRect(390, 70, 111, 22))
        self.key.setObjectName("key")
        self.duration = QtGui.QSpinBox(self.groupBox)
        self.duration.setGeometry(QtCore.QRect(390, 110, 111, 23))
        self.duration.setMinimum(1)
        self.duration.setMaximum(1000)
        self.duration.setProperty("value", QtCore.QVariant(1))
        self.duration.setObjectName("duration")
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(270, 110, 101, 17))
        self.label_9.setObjectName("label_9")
        self.swing = QtGui.QCheckBox(self.groupBox)
        self.swing.setGeometry(QtCore.QRect(30, 100, 83, 22))
        self.swing.setObjectName("swing")

        self.retranslateUi(blockDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), blockDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), blockDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(blockDialog)

    def retranslateUi(self, blockDialog):
        blockDialog.setWindowTitle(QtGui.QApplication.translate("blockDialog", "Edit Block", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("blockDialog", "Default settings", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("blockDialog", "Default resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("blockDialog", "Default BPM", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("blockDialog", "Default wildness", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("blockDialog", "Default key", None, QtGui.QApplication.UnicodeUTF8))
        self.duration.setStatusTip(QtGui.QApplication.translate("blockDialog", "How many times a block should be played", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("blockDialog", "Block duration", None, QtGui.QApplication.UnicodeUTF8))
        self.swing.setStatusTip(QtGui.QApplication.translate("blockDialog", "Swing the notes", None, QtGui.QApplication.UnicodeUTF8))
        self.swing.setText(QtGui.QApplication.translate("blockDialog", "Swing", None, QtGui.QApplication.UnicodeUTF8))

