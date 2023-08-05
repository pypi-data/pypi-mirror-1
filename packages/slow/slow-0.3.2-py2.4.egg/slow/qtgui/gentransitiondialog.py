# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'transitiondialog.ui'
#
# Created: Di Jan 31 21:27:33 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *
from custom_widgets import IterableComboBox as QComboBox

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x10" \
    "\x08\x06\x00\x00\x00\x1f\xf3\xff\x61\x00\x00\x02" \
    "\xe6\x49\x44\x41\x54\x38\x8d\x75\x92\x4b\x68\x5c" \
    "\x55\x18\xc7\x7f\xf7\x39\x77\x66\x6e\xae\xd3\x3a" \
    "\x4d\x62\xae\x4c\x5a\x4d\x14\x14\x6d\xd0\x48\x15" \
    "\x9f\x29\x52\x48\x57\x62\x45\xac\x88\xb4\x22\x14" \
    "\x44\x51\x54\x04\xb1\x15\x17\x8a\x8a\x96\x2e\x62" \
    "\x29\xba\x70\xe1\x42\x6a\xa8\xa9\xad\xc4\x9a\x9a" \
    "\xb6\x93\xaa\xe0\x22\xd6\xd0\x12\x0a\x13\xd3\x84" \
    "\x3c\x9c\x49\x26\xf3\xc8\x64\x66\x72\x33\xf7\x71" \
    "\x5c\xa4\x13\x5a\x6d\x7e\xf0\xad\xce\xf9\x7e\xe7" \
    "\x3b\xff\x73\x24\xae\xe1\x85\x53\xd5\xb6\x79\x43" \
    "\xfe\x44\x5e\xf1\x9d\x5c\xff\xb7\x2f\xb5\x6c\x7b" \
    "\xe6\x15\xd7\xf5\x47\x7e\xda\x1b\x4f\xb2\x0e\x12" \
    "\xc0\x9e\x41\xa7\x39\xf0\xc5\xab\x9e\x2b\x8a\x27" \
    "\x0d\xe3\x33\x12\x82\xd6\xf4\x4a\xae\x64\x28\x37" \
    "\x29\x35\x5f\xb5\x93\x97\x9e\xfa\xfd\xc0\xb6\x13" \
    "\xeb\x0a\xba\x4f\xaf\x1c\x1b\x4a\x68\xbb\x9a\x4b" \
    "\x3e\x93\x31\x05\x6b\xb4\x84\x39\x57\x41\xd6\x14" \
    "\xbc\x96\x28\xe6\xb2\x5f\x6d\xc8\xd6\x7e\x61\xc9" \
    "\xb9\xf2\xe7\xdb\x89\x37\xff\x27\xe8\x3c\x52\x1b" \
    "\x1b\x36\xb5\x36\x3a\xc0\x1e\x9c\x65\x53\xb1\x84" \
    "\x24\x05\xab\x1b\x64\x99\xd0\x46\x8b\xf1\x8e\x46" \
    "\xd4\x7f\xaa\x84\xfb\xbe\xdb\x3e\x7e\x74\xdf\xb9" \
    "\xba\x40\xde\xfd\x63\xe5\xc1\x44\x63\xcd\xb0\xa2" \
    "\x01\x6a\xc1\x67\x53\x65\x69\xba\xb6\xf8\xd7\x7b" \
    "\xce\xc2\xf0\x8b\x92\x9a\x3b\x14\xbe\x45\xcf\xa9" \
    "\x66\xc0\xd6\xa9\x02\x86\xae\xa2\x34\xde\xf3\xd0" \
    "\x75\x77\xe8\x3a\xbe\x7c\x8c\xf3\x42\x70\x5e\x08" \
    "\x6d\xc0\x13\xed\x7b\xfb\x3e\x00\xf4\xfa\xfa\x7d" \
    "\x1f\x7e\x6f\xef\x18\x48\xff\xd1\x9d\xcc\x8b\xee" \
    "\x33\x55\x61\xf6\x56\x84\xfd\xd1\xec\x44\xfc\xb1" \
    "\x03\x16\x80\xbc\x3c\x2f\xe2\xfc\x0d\x64\xc1\x15" \
    "\x0a\x72\xfb\xdd\x4f\x00\x5e\x5d\x70\x61\xff\xae" \
    "\x59\x59\x77\x76\x46\x6f\x8d\xce\x6d\x68\xd2\x10" \
    "\xb1\x30\xf9\x78\x6c\xb3\xde\xd8\xf9\x1c\x80\xac" \
    "\xca\x41\xc6\x9a\xf1\x51\x46\x05\x54\x60\xbe\xb5" \
    "\xf5\xf1\x47\x3e\x4f\xbd\x73\xed\x94\x3f\x77\x6d" \
    "\xc9\xab\x51\xfd\x0b\xdd\x50\x91\x1c\x09\xf3\xf2" \
    "\x54\x6a\xee\xd4\x6a\x0e\xb2\x19\xe4\xde\xbf\xab" \
    "\x3a\xf0\x72\xfb\x86\x52\x96\x0a\x14\xa4\x10\x63" \
    "\x4d\xad\x1f\xef\xf8\x26\xdb\xf3\xec\xf1\xa5\x78" \
    "\x5d\xa2\x3b\x4c\x66\x33\x50\x2e\x43\xc5\x6e\xbe" \
    "\x23\xf6\x74\xff\xee\xb5\x57\xe8\xea\xc9\x98\x33" \
    "\x7a\x24\x3d\xa6\x35\x98\xf5\x06\x03\xc1\xed\x61" \
    "\xcf\xbb\x39\x22\x8d\x68\xba\xe2\x15\x5d\xa9\xe3" \
    "\x62\x1e\xc3\x15\x80\x02\x66\xf2\xc2\xaf\xe5\xaf" \
    "\xef\xdf\xa9\x02\x04\xbe\x78\x72\xce\x36\x4c\x8a" \
    "\x40\x04\x30\xc0\xc9\x48\x8c\x16\x34\x95\x02\x9d" \
    "\xd7\xa5\xde\x02\xda\xc2\x22\x4c\x5c\x1a\x02\x6a" \
    "\x32\x80\xef\x8b\x41\x3b\x5d\x4c\x59\xcd\x0e\x5b" \
    "\xa6\xa6\xa7\x2d\xb9\x0a\x77\x02\xe2\x6a\xdd\xb6" \
    "\xda\x88\x80\x68\x72\x96\x50\xdf\xd9\x23\xe5\x73" \
    "\x7b\x7a\xd6\x04\xbf\xbd\xd5\x52\xd6\x53\x13\xdb" \
    "\xed\xde\x33\xef\x4e\xbc\x91\x78\xb8\xe9\x87\x91" \
    "\x7d\x66\xa6\x02\x12\xa8\x6e\x8d\x88\x53\x84\xad" \
    "\x02\x6c\xf0\xb4\x60\xb9\x36\x3e\xd0\x0b\xcc\xdf" \
    "\xe0\x67\xaf\xd2\xf6\x5a\x6a\x73\x43\xff\xa2\xe0" \
    "\x4a\x20\x36\xee\x4f\x4d\xc5\x1e\x3d\xf8\x7c\xe4" \
    "\xab\xb4\x17\x3a\x3c\xe3\x84\x1f\x38\xf8\x3a\xb0" \
    "\x96\x95\x7a\x23\x81\xef\x05\x0b\x0d\x27\x2f\x7f" \
    "\xa9\x0f\x85\xee\x75\xcf\x1e\x3d\x54\x1a\xfe\xf4" \
    "\x84\x65\x75\x94\xdd\xd1\xc3\xf9\x95\xc9\xbe\x8b" \
    "\x40\x79\xdd\xd3\xff\x43\xe8\x6a\xad\xcb\xbf\x59" \
    "\xcc\x31\xcf\x1e\x17\x60\x29\x00\x00\x00\x00\x49" \
    "\x45\x4e\x44\xae\x42\x60\x82"

class EDSMTransitionDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("EDSMTransitionDialog")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)

        EDSMTransitionDialogLayout = QGridLayout(self,1,1,11,6,"EDSMTransitionDialogLayout")

        self.object_name = QLineEdit(self,"object_name")

        EDSMTransitionDialogLayout.addMultiCellWidget(self.object_name,0,0,1,3)

        self.object_name_textlabel = QLabel(self,"object_name_textlabel")

        EDSMTransitionDialogLayout.addWidget(self.object_name_textlabel,0,0)

        self.message_type_textlabel = QLabel(self,"message_type_textlabel")

        EDSMTransitionDialogLayout.addWidget(self.message_type_textlabel,1,0)

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

        EDSMTransitionDialogLayout.addMultiCellLayout(Layout1,4,4,0,3)

        self.message_type = QComboBox(0,self,"message_type")

        EDSMTransitionDialogLayout.addMultiCellWidget(self.message_type,1,1,1,3)

        self.from_queue_textlabel = QLabel(self,"from_queue_textlabel")

        EDSMTransitionDialogLayout.addWidget(self.from_queue_textlabel,2,0)

        self.to_queue = QComboBox(0,self,"to_queue")
        self.to_queue.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,1,0,self.to_queue.sizePolicy().hasHeightForWidth()))

        EDSMTransitionDialogLayout.addWidget(self.to_queue,2,3)

        self.from_queue = QComboBox(0,self,"from_queue")
        self.from_queue.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,1,0,self.from_queue.sizePolicy().hasHeightForWidth()))

        EDSMTransitionDialogLayout.addWidget(self.from_queue,2,1)

        self.to_queue_textlabel = QLabel(self,"to_queue_textlabel")

        EDSMTransitionDialogLayout.addWidget(self.to_queue_textlabel,2,2)

        self.implementation_groupbox = QGroupBox(self,"implementation_groupbox")
        self.implementation_groupbox.setColumnLayout(0,Qt.Vertical)
        self.implementation_groupbox.layout().setSpacing(6)
        self.implementation_groupbox.layout().setMargin(11)
        implementation_groupboxLayout = QGridLayout(self.implementation_groupbox.layout())
        implementation_groupboxLayout.setAlignment(Qt.AlignTop)

        self.class_name = QComboBox(0,self.implementation_groupbox,"class_name")
        self.class_name.setEditable(1)
        self.class_name.setInsertionPolicy(QComboBox.NoInsertion)
        self.class_name.setAutoCompletion(1)
        self.class_name.setDuplicatesEnabled(0)

        implementation_groupboxLayout.addWidget(self.class_name,0,1)

        self.language_name = QComboBox(0,self.implementation_groupbox,"language_name")

        implementation_groupboxLayout.addWidget(self.language_name,1,1)

        self.init_code = QTextEdit(self.implementation_groupbox,"init_code")
        init_code_font = QFont(self.init_code.font())
        init_code_font.setFamily("Monospace")
        init_code_font.setPointSize(8)
        self.init_code.setFont(init_code_font)

        implementation_groupboxLayout.addWidget(self.init_code,2,1)

        self.class_name_textlabel = QLabel(self.implementation_groupbox,"class_name_textlabel")

        implementation_groupboxLayout.addWidget(self.class_name_textlabel,0,0)

        self.language_name_textlabel = QLabel(self.implementation_groupbox,"language_name_textlabel")

        implementation_groupboxLayout.addWidget(self.language_name_textlabel,1,0)

        self.init_code_textlabel = QLabel(self.implementation_groupbox,"init_code_textlabel")

        implementation_groupboxLayout.addWidget(self.init_code_textlabel,2,0)

        EDSMTransitionDialogLayout.addMultiCellWidget(self.implementation_groupbox,3,3,0,3)

        self.languageChange()

        self.resize(QSize(382,269).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
        self.connect(self.language_name,SIGNAL("activated(const QString&)"),self.language_name_activated)

        self.setTabOrder(self.object_name,self.buttonOk)
        self.setTabOrder(self.buttonOk,self.buttonCancel)
        self.setTabOrder(self.buttonCancel,self.buttonHelp)

        self.object_name_textlabel.setBuddy(self.object_name)
        self.init_code_textlabel.setBuddy(self.init_code)


    def languageChange(self):
        self.setCaption(self.__tr("EDSM Transition Dialog"))
        self.object_name_textlabel.setText(self.__tr("Name:"))
        self.message_type_textlabel.setText(self.__tr("Message Type:"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)
        self.from_queue_textlabel.setText(self.__tr("Source queue"))
        self.to_queue_textlabel.setText(self.__tr("Dest queue"))
        self.implementation_groupbox.setTitle(self.__tr("Implementation"))
        self.language_name.clear()
        self.language_name.insertItem(self.__tr("Python"))
        self.class_name_textlabel.setText(self.__tr("Class:"))
        self.language_name_textlabel.setText(self.__tr("Language:"))
        self.init_code_textlabel.setText(self.__tr("Init code:"))


    def language_name_activated(self,a0):
        print "EDSMTransitionDialog.language_name_activated(const QString&): Not implemented yet"

    def language_name_activated(self,a0):
        print "EDSMTransitionDialog.language_name_activated(const QString&): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("EDSMTransitionDialog",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = EDSMTransitionDialog()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
