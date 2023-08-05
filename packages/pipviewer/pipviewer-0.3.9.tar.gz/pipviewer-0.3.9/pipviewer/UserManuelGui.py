# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/usermanuelgui.ui'
#
# Created: Sun Nov 11 10:00:08 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.16
#
# WARNING! All changes made in this file will be lost!


from qt import *


class UserManuelGui(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("UserManuelGui")

        self.setAcceptDrops(1)

        UserManuelGuiLayout = QVBoxLayout(self,11,6,"UserManuelGuiLayout")

        self.txtBrwUserMan = QTextBrowser(self,"txtBrwUserMan")
        UserManuelGuiLayout.addWidget(self.txtBrwUserMan)

        self.languageChange()

        self.resize(QSize(610,583).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("User Manuel"))


    def __tr(self,s,c = None):
        return qApp.translate("UserManuelGui",s,c)
