# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'OpenDefiDlg.ui'
#
# Created: Sun May 31 22:10:05 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog.resize(411, 382)
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 411, 371))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.listWidget = QtGui.QListWidget(self.gridLayoutWidget)
        self.listWidget.setEnabled(True)
        self.listWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.listWidget.setProperty("showDropIndicator", QtCore.QVariant(False))
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 2, 0, 2, 2)
        self.dialogButtonBox = QtGui.QDialogButtonBox(self.gridLayoutWidget)
        self.dialogButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.dialogButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.dialogButtonBox.setObjectName("dialogButtonBox")
        self.gridLayout.addWidget(self.dialogButtonBox, 4, 0, 1, 2)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.dialogButtonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.dialogButtonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Select sections to ask for", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

