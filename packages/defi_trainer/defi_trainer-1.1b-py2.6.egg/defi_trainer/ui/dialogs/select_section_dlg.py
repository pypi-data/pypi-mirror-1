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

from defi_trainer.ui.dialogs.qt_des_select_section_dlg import Ui_Dialog
from PyQt4 import QtGui, QtCore

class SelectSectionDlg(QtGui.QDialog, Ui_Dialog):
    """
    This dialog asks the user for the definition section that
    should be asked for
    """
       
    def __init__(self, sections, parent = None):
        """
        @param sections: available sections
        @type sections: list of unicode strings
        """
        super(SelectSectionDlg, self).__init__(parent)
        self.setupUi(self)
        self.selection = list()
        self.connect(self, QtCore.SIGNAL("accepted()"), self.accepted)
        for item in sections:
            self.listWidget.addItem(item)

    def accepted(self):
        """
        Slot for OK button
        """
        list = self.listWidget.selectedItems()
        self.selection = [ x.text() for x in list]
        return
