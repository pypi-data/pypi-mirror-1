# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/scoregui.ui'
#
# Created: Sun Nov 11 10:00:06 2007
#      by: The PyQt User Interface Compiler (pyuic) 3.16
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ScoreGui(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ScoreGui")


        ScoreGuiLayout = QVBoxLayout(self,11,6,"ScoreGuiLayout")

        self.splitter1 = QSplitter(self,"splitter1")
        self.splitter1.setOrientation(QSplitter.Vertical)

        self.hitsLst = QListView(self.splitter1,"hitsLst")
        self.hitsLst.addColumn(self.__tr("target"))
        self.hitsLst.addColumn(self.__tr("%probe lenght"))
        self.hitsLst.addColumn(self.__tr("%id"))
        self.hitsLst.addColumn(self.__tr("Comment"))
        ScoreGuiLayout.addWidget(self.splitter1)

        layout17 = QHBoxLayout(None,0,6,"layout17")
        spacer9 = QSpacerItem(91,21,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout17.addItem(spacer9)

        self.okBtn = QPushButton(self,"okBtn")
        layout17.addWidget(self.okBtn)
        ScoreGuiLayout.addLayout(layout17)

        self.languageChange()

        self.resize(QSize(576,422).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okBtn,SIGNAL("clicked()"),self.accept)


    def languageChange(self):
        self.setCaption(self.__tr("Probe Score"))
        self.hitsLst.header().setLabel(0,self.__tr("target"))
        self.hitsLst.header().setLabel(1,self.__tr("%probe lenght"))
        self.hitsLst.header().setLabel(2,self.__tr("%id"))
        self.hitsLst.header().setLabel(3,self.__tr("Comment"))
        self.okBtn.setText(self.__tr("&OK"))
        self.okBtn.setAccel(QKeySequence(self.__tr("Alt+O")))


    def __tr(self,s,c = None):
        return qApp.translate("ScoreGui",s,c)
