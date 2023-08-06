"""
Copyright 2008,2009 Steven Mohr

This file is part of DefiTrainer.

    DefiTrainer is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DefiTrainer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DefiTrainer.  If not, see <http://www.gnu.org/licenses/>.
 
"""

from PyQt4 import QtGui, QtCore
from defi_trainer.ui.dialogs.qt_des_main_dialog import Ui_MainDlg
import random, copy, logging

class DefiDialog(QtGui.QDialog, Ui_MainDlg):
    """
    This is the main dialog of DefiTrainer. It asks for definitions of
    words and allows the user to track its learning progress.
    """

    def __init__(self, defis, parent = None):
        """
        @param defis: parser representation to convert
        @type defis: dictionary of list of tupels
        @param parent: parent of the dialog
        @type parent: PyQt4.QtGui.QWidget 
        """
        
        super(DefiDialog, self).__init__(parent)
        self.convert_defis(defis)
        self.all_defis = copy.deepcopy(self.defis)
        
        self.setupUi(self)
        self.label_word.setText(self.defis[0]['name'])
        self.connect(self.show_defi_button , QtCore.SIGNAL('clicked()'),
                     self.show_defi)
        
        self.connect(self.correct_defi_button , QtCore.SIGNAL('clicked()'),
                     self.action_defi_correct, QtCore.SLOT('trigger()'))
        self.connect(self.incorrect_defi_button , QtCore.SIGNAL('clicked()'),
                     self.action_defi_incorrect, QtCore.SLOT('trigger()'))
        
        self.connect(self.action_defi_correct, QtCore.SIGNAL('triggered()'),
                     self.correct_defi)
        self.connect(self.action_defi_incorrect, QtCore.SIGNAL('triggered()'),
                     self.next_defi)
        
        self.correct_shortcut = QtGui.QShortcut(QtGui.QKeySequence(self.tr("r")), self)
        self.incorrect_shortcut = QtGui.QShortcut(QtGui.QKeySequence(self.tr("w")), self)
        self.connect(self.correct_shortcut, QtCore.SIGNAL('activated()'),
                     self.action_defi_correct, QtCore.SLOT('trigger()'))
        self.connect(self.incorrect_shortcut, QtCore.SIGNAL('activated()'),
                     self.action_defi_incorrect, QtCore.SLOT('trigger()'))
        
        self.defis_right = 0
        self.update_stats()


    def convert_defis(self, defis):
        """
        Converts the definitions from its parser representation
        to a new GUI representation.
        @param defis: parser representation to convert
        @type defis: dictionary of list of tupels  
        """

        temp = []
        for section, element in defis.iteritems():
            for item in element:
                new_element = {}
                new_element['name'] = unicode(item[0])
                if section != '__STANDARD__':
                    new_element['name'] += u" (%s)" % section
                new_element['defi'] = ''
                for string in item[1]:
                    new_element['defi'] +=  unicode(string) + u' '
                temp.append(new_element)
        self.defis = temp
        self.num_defis = len(self.defis)

    def correct_defi(self):
        """
        Slot for the "Definition Correct" button
        """
        self.defis_right += 1
        del self.defis[0]
        if len(self.defis) == 0:
            QtGui.QMessageBox.information(
                                          self,
                                          self.tr("All definitions correct!"),
                                          self.tr("All definitions correct. Let's"\
                                                     " start again!")
                                          )
            self.defis = copy.deepcopy(self.all_defis)
            self.defis_right = 0

        self.update_stats()
        self.next_defi()

    def next_defi(self):
        """
        Slot for the "Next Definition" button
        """
        random.shuffle(self.defis)
        self.label_word.setText(self.defis[0]['name'])
        self.edit_defi.setHtml("")
        self.incorrect_defi_button.setEnabled(False)
        self.correct_defi_button.setEnabled(False)
        self.action_defi_incorrect.setEnabled(False)
        self.action_defi_correct.setEnabled(False)
        self.show_defi_button.setEnabled(True)

    def show_defi(self):
        """
        Slot for the "Show Definition" button
        """
        self.edit_defi.setHtml(self.defis[0]['defi'])
        self.incorrect_defi_button.setEnabled(True)
        self.correct_defi_button.setEnabled(True)
        self.action_defi_incorrect.setEnabled(True)
        self.action_defi_correct.setEnabled(True)
        self.show_defi_button.setEnabled(False)

    def update_stats(self):
        """
        Updates the stats label to show the correct questions
        / right answers ratio.
        """
        string = "%i / %i" % (self.defis_right ,self.num_defis)
        self.label_stats.setText(string)

