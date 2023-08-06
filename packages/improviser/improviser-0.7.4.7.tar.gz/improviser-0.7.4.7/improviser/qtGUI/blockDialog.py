# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'block.ui'
#
# Created: Wed Jan  7 13:25:17 2009
#      by: PyQt4 UI code generator 4.4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_blockDialog(object):
    def setupUi(self, blockDialog):
        blockDialog.setObjectName("blockDialog")
        blockDialog.resize(369, 224)
        blockDialog.setModal(True)
        self.buttonBox = QtGui.QDialogButtonBox(blockDialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtGui.QLabel(blockDialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 111, 17))
        self.label.setObjectName("label")
        self.label_2 = QtGui.QLabel(blockDialog)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 91, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtGui.QLabel(blockDialog)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 131, 17))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtGui.QLabel(blockDialog)
        self.label_4.setGeometry(QtCore.QRect(20, 140, 121, 17))
        self.label_4.setObjectName("label_4")
        self.comboBox = QtGui.QComboBox(blockDialog)
        self.comboBox.setGeometry(QtCore.QRect(170, 20, 181, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox_2 = QtGui.QComboBox(blockDialog)
        self.comboBox_2.setGeometry(QtCore.QRect(170, 60, 181, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        self.comboBox_3 = QtGui.QComboBox(blockDialog)
        self.comboBox_3.setGeometry(QtCore.QRect(170, 100, 181, 22))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_4 = QtGui.QComboBox(blockDialog)
        self.comboBox_4.setGeometry(QtCore.QRect(170, 140, 181, 22))
        self.comboBox_4.setObjectName("comboBox_4")

        self.retranslateUi(blockDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), blockDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), blockDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(blockDialog)

    def retranslateUi(self, blockDialog):
        blockDialog.setWindowTitle(QtGui.QApplication.translate("blockDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("blockDialog", "Wildness function", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("blockDialog", "BPM function", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("blockDialog", "Progression function", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("blockDialog", "Resolution function", None, QtGui.QApplication.UnicodeUTF8))

