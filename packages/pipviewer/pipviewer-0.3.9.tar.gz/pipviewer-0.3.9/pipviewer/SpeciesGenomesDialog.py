#!/usr/bin/python
#  Copyright (C) 2006-2007 Free Software Foundation

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


#############################################################
#            I M P O R T I N G   M O D U L E S
#############################################################

import os
import sys

from qt import *
from SpeciesGenomesGui import SpeciesGenomesGui


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

SPECIES_COLLUMN = 1
ACC_COLLUMN = 2


#############################################################
#                  M A I N   C L A S S
#############################################################

class SpeciesGenomesDialog(SpeciesGenomesGui):
    """ This class define a SpeciesGenomesWidget for visualise and associating
    accession number of different species genomes. Accession number are unique
    ids used for identify biological sequence on the NCBI internet database.
    """
    def __init__(self,parent=None,name=None):
        SpeciesGenomesGui.__init__(self, parent, name)
        self.connect(self.genomesLst, SIGNAL("doubleClicked(QListViewItem *, const QPoint &, int)"),
                    self.setAccNumber)
        self.connect(self.helpBtn, SIGNAL("clicked()"), self.show_help)
    
    
    def setAccNumber(self, item):
        """ Mutator for setting the accession number on the speciesGenomes view
        list. Take the double-clicked list view item as parameter.
        """
        userText = QInputDialog.getText(item.text(SPECIES_COLLUMN), 
                    "Please enter the accession number for this genome")
        if (userText[1] == True):
            item.setText(ACC_COLLUMN, unicode(userText[0]))

    
    def show_help(self):
        """ Action performed when the user press the 'Help' button.
        """
        msg = "To enter the genome accession number of a particular specie,\nsimply double-click on the selected item."
        QMessageBox.information(self, "Help", msg)
                   

#Self Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SpeciesGenomesDialog()
    win.show()
    app.exec_loop()
