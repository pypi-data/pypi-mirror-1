# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'prefdialog.ui'
#
# Created: Di Jan 31 21:27:33 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *

class PrefDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("PrefDialog")

        self.setSizeGripEnabled(1)

        PrefDialogLayout = QVBoxLayout(self,11,6,"PrefDialogLayout")
        PrefDialogLayout.setResizeMode(QLayout.Fixed)

        self.prefframes = QTabWidget(self,"prefframes")

        self.path = QWidget(self.prefframes,"path")
        self.prefframes.insertTab(self.path,QString.fromLatin1(""))

        self.xml = QWidget(self.prefframes,"xml")

        self.optimize_xml_size = QCheckBox(self.xml,"optimize_xml_size")
        self.optimize_xml_size.setGeometry(QRect(8,8,264,17))
        self.prefframes.insertTab(self.xml,QString.fromLatin1(""))

        self.display = QWidget(self.prefframes,"display")

        self.auto_update_edsm_graph = QCheckBox(self.display,"auto_update_edsm_graph")
        self.auto_update_edsm_graph.setGeometry(QRect(8,8,352,17))
        self.prefframes.insertTab(self.display,QString.fromLatin1(""))

        self.available_protocols = QWidget(self.prefframes,"available_protocols")
        available_protocolsLayout = QHBoxLayout(self.available_protocols,11,6,"available_protocolsLayout")

        self.protocols = QTextEdit(self.available_protocols,"protocols")
        self.protocols.setEnabled(0)
        self.protocols.setTextFormat(QTextEdit.PlainText)
        self.protocols.setWordWrap(QTextEdit.NoWrap)
        available_protocolsLayout.addWidget(self.protocols)
        self.prefframes.insertTab(self.available_protocols,QString.fromLatin1(""))

        self.available_languages = QWidget(self.prefframes,"available_languages")
        available_languagesLayout = QHBoxLayout(self.available_languages,11,6,"available_languagesLayout")

        self.languages = QTextEdit(self.available_languages,"languages")
        self.languages.setEnabled(1)
        self.languages.setTextFormat(QTextEdit.PlainText)
        self.languages.setWordWrap(QTextEdit.NoWrap)
        available_languagesLayout.addWidget(self.languages)
        self.prefframes.insertTab(self.available_languages,QString.fromLatin1(""))
        PrefDialogLayout.addWidget(self.prefframes)

        Layout1 = QHBoxLayout(None,0,6,"Layout1")

        self.buttonHelp = QPushButton(self,"buttonHelp")
        self.buttonHelp.setAutoDefault(1)
        Layout1.addWidget(self.buttonHelp)
        Horizontal_Spacing2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(Horizontal_Spacing2)

        self.buttonOk = QPushButton(self,"buttonOk")
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        Layout1.addWidget(self.buttonOk)

        self.buttonCancel = QPushButton(self,"buttonCancel")
        self.buttonCancel.setAutoDefault(1)
        Layout1.addWidget(self.buttonCancel)
        PrefDialogLayout.addLayout(Layout1)

        self.languageChange()

        self.resize(QSize(403,261).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)


    def languageChange(self):
        self.setCaption(self.__tr("Preferences"))
        self.prefframes.changeTab(self.path,self.__tr("Path"))
        self.optimize_xml_size.setText(self.__tr("Optimize XML output for size"))
        self.prefframes.changeTab(self.xml,self.__tr("XML"))
        self.auto_update_edsm_graph.setText(self.__tr("Automatically update EDSM graph"))
        self.prefframes.changeTab(self.display,self.__tr("Display"))
        self.protocols.setText(self.__tr("UDP\n"
"TCP"))
        self.prefframes.changeTab(self.available_protocols,self.__tr("Protocols"))
        self.languages.setText(self.__tr("Python\n"
"Java\n"
"C++\n"
"C\n"
""))
        self.prefframes.changeTab(self.available_languages,self.__tr("Languages"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)


    def __tr(self,s,c = None):
        return qApp.translate("PrefDialog",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = PrefDialog()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
