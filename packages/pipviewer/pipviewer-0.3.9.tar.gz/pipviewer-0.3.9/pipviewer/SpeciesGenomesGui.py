# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/speciesgenomesgui.ui'
#
# Created: Sun Nov 11 10:00:08 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.16
#
# WARNING! All changes made in this file will be lost!


from qt import *


class SpeciesGenomesGui(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("SpeciesGenomesGui")

        self.setFocusPolicy(QDialog.NoFocus)
        self.setModal(1)

        SpeciesGenomesGuiLayout = QVBoxLayout(self,11,6,"SpeciesGenomesGuiLayout")

        self.genomesLst = QListView(self,"genomesLst")
        self.genomesLst.addColumn(self.__tr("#"))
        self.genomesLst.addColumn(self.__tr("Name"))
        self.genomesLst.addColumn(self.__tr("Accesion Number"))
        self.genomesLst.setSelectionMode(QListView.Single)
        self.genomesLst.setAllColumnsShowFocus(1)
        SpeciesGenomesGuiLayout.addWidget(self.genomesLst)

        layout12 = QHBoxLayout(None,0,6,"layout12")

        self.helpBtn = QPushButton(self,"helpBtn")
        layout12.addWidget(self.helpBtn)
        spacer1 = QSpacerItem(229,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout12.addItem(spacer1)

        self.cancelBtn = QPushButton(self,"cancelBtn")
        layout12.addWidget(self.cancelBtn)

        self.okBtn = QPushButton(self,"okBtn")
        layout12.addWidget(self.okBtn)
        SpeciesGenomesGuiLayout.addLayout(layout12)

        self.languageChange()

        self.resize(QSize(419,486).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okBtn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelBtn,SIGNAL("clicked()"),self.reject)


    def languageChange(self):
        self.setCaption(self.__tr("Species Genomes"))
        self.genomesLst.header().setLabel(0,self.__tr("#"))
        self.genomesLst.header().setLabel(1,self.__tr("Name"))
        self.genomesLst.header().setLabel(2,self.__tr("Accesion Number"))
        self.helpBtn.setText(self.__tr("&Help"))
        self.helpBtn.setAccel(QKeySequence(self.__tr("Alt+H")))
        self.cancelBtn.setText(self.__tr("&Cancel"))
        self.cancelBtn.setAccel(QKeySequence(self.__tr("Alt+C")))
        self.okBtn.setText(self.__tr("&OK"))
        self.okBtn.setAccel(QKeySequence(self.__tr("Alt+O")))


    def __tr(self,s,c = None):
        return qApp.translate("SpeciesGenomesGui",s,c)
