# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainDialog.ui'
#
# Created: Sun May 31 22:10:05 2009
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainDlg(object):
    def setupUi(self, MainDlg):
        MainDlg.setObjectName("MainDlg")
        MainDlg.setWindowModality(QtCore.Qt.NonModal)
        MainDlg.resize(725, 387)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainDlg.sizePolicy().hasHeightForWidth())
        MainDlg.setSizePolicy(sizePolicy)
        MainDlg.setSizeGripEnabled(True)
        self.gridLayout_2 = QtGui.QGridLayout(MainDlg)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridFrame = QtGui.QFrame(MainDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.gridFrame.sizePolicy().hasHeightForWidth())
        self.gridFrame.setSizePolicy(sizePolicy)
        self.gridFrame.setMinimumSize(QtCore.QSize(400, 200))
        self.gridFrame.setSizeIncrement(QtCore.QSize(20, 20))
        self.gridFrame.setObjectName("gridFrame")
        self.gridLayout = QtGui.QGridLayout(self.gridFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.label_word = QtGui.QLabel(self.gridFrame)
        self.label_word.setText("Defi")
        self.label_word.setObjectName("label_word")
        self.gridLayout.addWidget(self.label_word, 0, 0, 1, 1)
        self.label_stats = QtGui.QLabel(self.gridFrame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_stats.sizePolicy().hasHeightForWidth())
        self.label_stats.setSizePolicy(sizePolicy)
        self.label_stats.setText("0 / 0")
        self.label_stats.setObjectName("label_stats")
        self.gridLayout.addWidget(self.label_stats, 0, 1, 1, 1)
        self.show_defi_button = QtGui.QPushButton(self.gridFrame)
        self.show_defi_button.setDefault(True)
        self.show_defi_button.setObjectName("show_defi_button")
        self.gridLayout.addWidget(self.show_defi_button, 1, 0, 1, 1)
        self.edit_defi = QtGui.QTextEdit(self.gridFrame)
        self.edit_defi.setReadOnly(True)
        self.edit_defi.setObjectName("edit_defi")
        self.gridLayout.addWidget(self.edit_defi, 2, 0, 1, 1)
        self.correct_defi_button = QtGui.QPushButton(self.gridFrame)
        self.correct_defi_button.setEnabled(False)
        self.correct_defi_button.setObjectName("correct_defi_button")
        self.gridLayout.addWidget(self.correct_defi_button, 3, 1, 1, 1)
        self.incorrect_defi_button = QtGui.QPushButton(self.gridFrame)
        self.incorrect_defi_button.setEnabled(False)
        self.incorrect_defi_button.setObjectName("incorrect_defi_button")
        self.gridLayout.addWidget(self.incorrect_defi_button, 3, 2, 1, 1)
        self.gridLayout_2.addWidget(self.gridFrame, 0, 0, 1, 1)
        self.action_defi_correct = QtGui.QAction(MainDlg)
        self.action_defi_correct.setCheckable(False)
        self.action_defi_correct.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.action_defi_correct.setObjectName("action_defi_correct")
        self.action_defi_incorrect = QtGui.QAction(MainDlg)
        self.action_defi_incorrect.setCheckable(False)
        self.action_defi_incorrect.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.action_defi_incorrect.setObjectName("action_defi_incorrect")

        self.retranslateUi(MainDlg)
        QtCore.QMetaObject.connectSlotsByName(MainDlg)

    def retranslateUi(self, MainDlg):
        MainDlg.setWindowTitle(QtGui.QApplication.translate("MainDlg", "DefiTrainer 1.1", None, QtGui.QApplication.UnicodeUTF8))
        self.show_defi_button.setText(QtGui.QApplication.translate("MainDlg", "Show definition", None, QtGui.QApplication.UnicodeUTF8))
        self.correct_defi_button.setText(QtGui.QApplication.translate("MainDlg", "Definition &correct", None, QtGui.QApplication.UnicodeUTF8))
        self.incorrect_defi_button.setText(QtGui.QApplication.translate("MainDlg", "Definition &wrong", None, QtGui.QApplication.UnicodeUTF8))
        self.action_defi_correct.setText(QtGui.QApplication.translate("MainDlg", "defiCorrect", None, QtGui.QApplication.UnicodeUTF8))
        self.action_defi_correct.setShortcut(QtGui.QApplication.translate("MainDlg", "R", None, QtGui.QApplication.UnicodeUTF8))
        self.action_defi_incorrect.setText(QtGui.QApplication.translate("MainDlg", "defiIncorrect", None, QtGui.QApplication.UnicodeUTF8))
        self.action_defi_incorrect.setShortcut(QtGui.QApplication.translate("MainDlg", "L", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainDlg = QtGui.QDialog()
    ui = Ui_MainDlg()
    ui.setupUi(MainDlg)
    MainDlg.show()
    sys.exit(app.exec_())

