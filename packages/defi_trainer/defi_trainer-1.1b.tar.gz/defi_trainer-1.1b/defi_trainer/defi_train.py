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
import sys, codecs
from defi_trainer.ui.dialogs.main_dialog import DefiDialog
from defi_trainer.ui.dialogs.select_section_dlg import SelectSectionDlg
from defi_trainer.parser.defis import Defis
import defi_trainer.resources

class DefiTrainer(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.actModel = dict()
        self.app = QtGui.QApplication(sys.argv)
        locale = QtCore.QLocale.system().name()
        self.translator = QtCore.QTranslator()
        selected_sections = list()
        if self.translator.load("defi_trainer_" + locale, ":/"):
            self.app.installTranslator(self.translator)
        
        file_name = ""
        while len(file_name) == 0:
            file_name = QtGui.QFileDialog.getOpenFileName(None, self.tr("Open definition file"))
        
        self.model = Defis(codecs.open(file_name, "r", "UTF-8").read())
        
        
        if len(self.model.get_section_list()) > 1:
            self.select_diag = SelectSectionDlg(self.model.get_section_list(),
                                         None)
            self.select_diag.exec_()
            selected_sections = self.select_diag.selection
            if len(self.select_diag.selection) == 0:
                self.select_diag.selection = self.model.get_section_list()
        else:
            selected_sections = self.model.get_section_list()
                                          
        for key, item in self.model.data.iteritems():
            if key in selected_sections:
                self.actModel[key] = item
        self.dialog = DefiDialog(self.actModel)
        self.dialog.show()
        self.app.exec_()
