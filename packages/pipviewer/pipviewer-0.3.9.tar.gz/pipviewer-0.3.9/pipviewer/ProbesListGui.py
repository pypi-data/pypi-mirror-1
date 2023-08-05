# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/probeslistgui.ui'
#
# Created: Sun Nov 11 10:00:08 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.16
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ProbesListGui(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ProbesListGui")


        ProbesListGuiLayout = QVBoxLayout(self,11,6,"ProbesListGuiLayout")

        self.lstViewProbesList = QListView(self,"lstViewProbesList")
        self.lstViewProbesList.addColumn(self.__tr("#"))
        self.lstViewProbesList.addColumn(self.__tr("Probe name"))
        self.lstViewProbesList.addColumn(self.__tr("Start"))
        self.lstViewProbesList.addColumn(self.__tr("End"))
        self.lstViewProbesList.addColumn(self.__tr("Length"))
        self.lstViewProbesList.setAllColumnsShowFocus(1)
        ProbesListGuiLayout.addWidget(self.lstViewProbesList)

        layout2 = QHBoxLayout(None,0,6,"layout2")

        self.helpBtn = QPushButton(self,"helpBtn")
        layout2.addWidget(self.helpBtn)
        spacer1 = QSpacerItem(200,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout2.addItem(spacer1)

        self.closeBtn = QPushButton(self,"closeBtn")
        layout2.addWidget(self.closeBtn)
        ProbesListGuiLayout.addLayout(layout2)

        self.languageChange()

        self.resize(QSize(401,452).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closeBtn,SIGNAL("pressed()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("Probes List"))
        self.lstViewProbesList.header().setLabel(0,self.__tr("#"))
        self.lstViewProbesList.header().setLabel(1,self.__tr("Probe name"))
        self.lstViewProbesList.header().setLabel(2,self.__tr("Start"))
        self.lstViewProbesList.header().setLabel(3,self.__tr("End"))
        self.lstViewProbesList.header().setLabel(4,self.__tr("Length"))
        self.helpBtn.setText(self.__tr("Help"))
        self.closeBtn.setText(self.__tr("&Close"))
        self.closeBtn.setAccel(QKeySequence(self.__tr("Alt+C")))


    def __tr(self,s,c = None):
        return qApp.translate("ProbesListGui",s,c)
