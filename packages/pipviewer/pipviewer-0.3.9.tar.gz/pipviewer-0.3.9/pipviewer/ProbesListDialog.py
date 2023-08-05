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
from ProbesListGui import ProbesListGui


#############################################################
#              G L O B A L   C O N S T A N T S
#############################################################

# Probe position
PROBE_START_POS = 2
PROBE_STOP_POS = 3

# Mouse signlal
SELECT_SIG = SIGNAL("doubleClicked(QListViewItem *, const QPoint &, int)")

#############################################################
#                  M A I N   C L A S S
#############################################################

class ProbesListDialog(ProbesListGui):
    """ This class define a ProbesListDialog for visualise and selecting 
    probes that has been set in the mapping.
    """
    def __init__(self,parent=None,name=None):
        ProbesListGui.__init__(self, parent, name)
        self.connect(self.helpBtn, SIGNAL("clicked()"), self.show_help)
     

    def show_help(self):
        """ Action performed when the user press the 'Help' button.
        """
        msg = "To access a probe location on the conservation viewer,\nsimply double-click on the selected item."
        QMessageBox.information(self, "Help", msg)
                   

#Self Test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ProbesListDialog()
    win.show()
    app.exec_loop()
