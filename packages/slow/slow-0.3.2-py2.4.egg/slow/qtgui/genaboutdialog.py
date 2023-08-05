# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutdialog.ui'
#
# Created: Di Jan 31 21:27:30 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x10" \
    "\x08\x06\x00\x00\x00\x1f\xf3\xff\x61\x00\x00\x01" \
    "\xac\x49\x44\x41\x54\x38\x8d\xc5\xd3\x3f\x48\x55" \
    "\x01\x14\xc7\xf1\xcf\xbd\xef\xbe\xe7\x43\x09\x85" \
    "\x47\x86\xa9\x39\xbc\x41\x08\x6a\x10\xca\x6a\x08" \
    "\x6c\x6f\xb3\xda\x42\x4a\xa4\x29\x82\xa0\x90\x96" \
    "\xa0\xa5\xcd\x96\x96\x1a\x84\xa2\xa5\x16\x03\xe1" \
    "\x35\x84\x5b\x42\xba\x54\xd0\x1f\xb0\xa0\x4c\x30" \
    "\x5e\x68\x2f\xcb\x7c\xff\xae\xb7\xa1\x40\x93\xb4" \
    "\xc1\xa1\xb3\x9c\xdf\x19\xbe\x1c\xf8\x9d\xdf\x09" \
    "\x92\x24\xb1\x9d\x0a\xb7\x45\x23\x30\xa2\x53\xdd" \
    "\x47\xcb\xf8\x81\x15\xd4\x11\x21\x83\xf4\x3a\x1d" \
    "\xfd\x9e\x33\xf2\x99\x06\x67\x53\x29\xfb\x22\xb1" \
    "\x87\xea\xae\xa0\xb0\xe5\xaa\x04\xab\x76\xe3\x8c" \
    "\xba\xa1\x6a\x5d\x39\x88\x9c\x08\xc3\x38\xac\xa5" \
    "\xb3\xe9\xbb\x6a\xfa\x36\x05\xab\x72\xb8\xdc\xd2" \
    "\xd1\x32\xd1\xd6\xd1\x76\xcd\x8a\x59\x15\xc7\xf0" \
    "\x3c\x4c\x96\x92\xfb\xb9\xbd\xb9\x5c\x76\x4f\xf6" \
    "\x8e\xb2\xc3\x82\x75\x70\xcd\x2e\xb1\x73\x51\x7b" \
    "\xf4\xa4\xfd\x78\xfb\xf5\xe6\xce\xe6\xee\xe2\x4c" \
    "\xb1\xa0\xe2\xa4\xc0\x1c\x44\x49\x29\x99\x5e\x2c" \
    "\x2f\x56\xc3\xfe\xb0\xc3\xa2\x7b\xde\xeb\xc7\x2b" \
    "\x55\x03\xba\x0c\x04\x47\x82\xde\xcc\x81\x8c\xd2" \
    "\xd3\x92\xe5\xc2\xf2\x03\x29\x43\xb2\x4a\x6b\x26" \
    "\x0e\x6a\xd5\xa5\xe0\x82\x1e\x45\x8c\x7a\x67\xc5" \
    "\x82\xa3\x0e\x3a\x84\x9d\x18\xc3\xb8\x1b\x1a\x5d" \
    "\xb5\xc3\x57\x19\x64\x09\x1a\x89\xac\x2a\x7a\x6b" \
    "\xca\x6b\x3d\xba\x71\x4a\x5e\x28\xaf\x0d\x35\xdc" \
    "\x54\x37\x65\x44\x83\x61\x29\xf1\x46\x8b\x42\x15" \
    "\x7c\x37\xed\x85\x58\x11\x0d\x68\xc2\x07\xdc\xc2" \
    "\x84\x61\x89\x4b\x7f\x83\x21\xf2\x0d\xb1\x49\xcf" \
    "\x2c\xd8\xaf\x55\x1a\x73\x18\x53\x36\xe3\xbc\x26" \
    "\xb7\xb7\x8a\x5b\x24\x46\xec\x8d\x39\x2f\x7d\xd2" \
    "\xaa\x8a\x71\x5f\xcc\xba\xa8\xd1\xe8\xbf\xb2\x1a" \
    "\xa9\x61\x15\x15\x13\x26\xf5\x99\xf7\xd9\xac\xd3" \
    "\x22\x8f\xfe\x38\xe9\x26\x95\x92\x47\x80\x44\xd9" \
    "\xbc\x5e\x4b\x06\x45\x1e\x0b\xac\x45\x77\x63\x4f" \
    "\xfd\xd2\x41\x9a\xe0\xbf\x7f\xe3\x4f\xae\x03\x8b" \
    "\xee\x04\xa5\xca\xcf\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"

class AboutDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("AboutDialog")

        self.setMinimumSize(QSize(300,200))

        AboutDialogLayout = QVBoxLayout(self,6,6,"AboutDialogLayout")
        AboutDialogLayout.setResizeMode(QLayout.Minimum)

        self.frame11 = QFrame(self,"frame11")
        self.frame11.setFrameShape(QFrame.StyledPanel)
        self.frame11.setFrameShadow(QFrame.Raised)
        frame11Layout = QVBoxLayout(self.frame11,6,6,"frame11Layout")

        self.title_label = QLabel(self.frame11,"title_label")
        self.title_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum,0,0,self.title_label.sizePolicy().hasHeightForWidth()))
        self.title_label.setTextFormat(QLabel.RichText)
        self.title_label.setAlignment(QLabel.AlignVCenter)
        frame11Layout.addWidget(self.title_label)

        self.text_label = QLabel(self.frame11,"text_label")
        self.text_label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.text_label.sizePolicy().hasHeightForWidth()))
        frame11Layout.addWidget(self.text_label)

        self.running_psyco_textLabel = QLabel(self.frame11,"running_psyco_textLabel")
        self.running_psyco_textLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.running_psyco_textLabel.sizePolicy().hasHeightForWidth()))
        self.running_psyco_textLabel.setAlignment(QLabel.AlignCenter)
        frame11Layout.addWidget(self.running_psyco_textLabel)
        AboutDialogLayout.addWidget(self.frame11)

        self.about_ok_button = QPushButton(self,"about_ok_button")
        self.about_ok_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.about_ok_button.sizePolicy().hasHeightForWidth()))
        self.about_ok_button.setDefault(1)
        self.about_ok_button.setIconSet(QIconSet(self.image0))
        self.about_ok_button.setFlat(0)
        AboutDialogLayout.addWidget(self.about_ok_button)

        self.languageChange()

        self.resize(QSize(323,200).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.about_ok_button,SIGNAL("clicked()"),self.about_ok_button_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("About ..."))
        self.title_label.setText(self.__tr("<p align=\"center\"><font size=\"+3\"><b>S<font size=\"+2\">LOSL</font> Overlay Workbench V[VT]</b></font>\n"
"<br />\n"
"<br />\n"
"<b>by Stefan Behnel</b>\n"
"<br />\n"
"<br />\n"
"Designing overlays in no-time!</p>"))
        self.text_label.setText(QString.null)
        self.running_psyco_textLabel.setText(self.__tr("- running psyco -"))
        self.about_ok_button.setText(self.__tr("&OK"))
        self.about_ok_button.setAccel(self.__tr("Alt+O"))


    def about_ok_button_clicked(self):
        print "AboutDialog.about_ok_button_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("AboutDialog",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = AboutDialog()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
