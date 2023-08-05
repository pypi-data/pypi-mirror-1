# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'statedialog.ui'
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
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x10" \
    "\x08\x06\x00\x00\x00\x1f\xf3\xff\x61\x00\x00\x02" \
    "\x17\x49\x44\x41\x54\x38\x8d\xa5\x93\xbf\x4b\x1c" \
    "\x41\x18\x86\x9f\x99\xdd\xbb\x5d\xcd\x9d\x24\x39" \
    "\x04\x51\x48\x0c\x1c\xa8\xd8\xd8\x26\x6d\x20\x4d" \
    "\x38\x08\x81\xe0\x1f\x91\xc6\xb3\x4c\x61\x61\x61" \
    "\x7b\xfe\x01\x76\x76\x69\x85\x58\x98\x88\xd7\xe4" \
    "\x8c\x86\xfc\x40\x50\xd2\x24\x06\x84\x95\x80\x84" \
    "\x35\xba\xee\xee\xec\xce\x97\xe2\x72\xa7\xe7\xd9" \
    "\xe5\x6d\x66\x18\xe6\x7d\xe6\xfb\xe6\x9d\x51\x8d" \
    "\x46\x43\xf8\x0f\xb9\x00\x73\x73\x73\x6c\x6f\x0b" \
    "\x22\x82\x31\x0a\xd7\x85\xbd\x3d\x61\x7f\x1f\xd2" \
    "\x14\x8c\xd1\x7d\xc6\x95\x15\x58\x5e\x5e\x6e\x03" \
    "\x00\xa6\xa7\x05\x11\x85\x48\x7b\x9c\x98\x00\x63" \
    "\x04\xa5\x04\x91\x1c\xa5\xda\x73\x63\x84\x3c\x17" \
    "\x60\xe0\xb2\x02\x80\x72\xb9\x73\x8a\x22\xb7\x16" \
    "\x80\xcc\x0a\xd6\x64\x44\x91\x25\x4d\x2d\xc7\xc7" \
    "\x96\x72\x59\x18\x1e\xbf\xd5\xdb\xc2\x4d\x3a\x0e" \
    "\x52\x0e\x0e\x72\x4e\x4f\xc1\xf7\x5d\x3c\xaf\x48" \
    "\x18\x1a\xa6\xa6\x12\x6c\x1c\x43\xa9\x04\x40\x5f" \
    "\x73\x26\xcb\xf8\xfc\xe9\x82\xcd\xcd\x0c\x11\x61" \
    "\x72\x12\x44\x0c\x51\xa4\x29\x14\x0c\x63\x63\x0e" \
    "\xc9\xf9\x79\x77\x7f\x0f\x20\xb7\x96\xaf\x5f\x12" \
    "\x5a\x2d\x87\x6a\x15\x1e\x3d\x1e\xe4\xde\x03\x4d" \
    "\x9a\x6a\x4e\x4e\x84\x91\x11\x4b\xea\x68\xd4\x15" \
    "\x4f\x0f\xe0\xc7\xf7\x84\x66\xd3\xa1\x52\xc9\x99" \
    "\x99\x71\xd1\x40\x70\x64\x38\x3a\x72\x49\x12\xc3" \
    "\xe8\x28\xd8\x34\xc5\x71\x9c\x7e\x40\x62\x2d\xbb" \
    "\xbb\x42\x18\x16\xa8\x56\x41\x7b\x45\x52\x60\x67" \
    "\x07\x0e\x0f\x5d\xac\xcd\x28\x0d\x0f\x82\xd6\xa0" \
    "\x2e\x6b\xe8\x5e\xe2\x9d\x0f\x0e\x8c\x03\xe3\xf0" \
    "\x54\x42\xfe\x84\x21\xcd\x0d\xcd\xd6\xdb\x32\xe2" \
    "\x68\x2a\x15\xc3\xc7\xa6\x25\x08\x2c\xcf\x9e\xfb" \
    "\x37\xa7\xb0\x56\x5d\xa0\xb6\xba\xc8\xda\xcf\x22" \
    "\x8e\x9b\x61\x74\x46\x41\x09\x0a\x68\xbd\x1b\xe0" \
    "\xf6\xdd\x98\x27\x35\xcb\x59\x12\x53\x2a\xb5\xa3" \
    "\x54\x03\xef\x91\xeb\x80\x8e\xbe\xbd\x08\x79\xf3" \
    "\x5a\xa3\x95\xc3\xfd\x89\x0b\x7e\x9f\x6d\xf4\x24" \
    "\x16\x04\x41\x1b\xb0\x56\x5d\xb8\x9e\x26\xb5\xd5" \
    "\x45\x7e\xbd\x8c\xc9\x93\x84\xa2\xef\x73\x1a\xc7" \
    "\x6c\xad\xaf\x33\x3b\x3b\x0b\xb4\x9f\x71\xbd\x5e" \
    "\x2f\xba\xb4\xa0\xd6\x5a\x84\x87\xfd\x15\xb8\x22" \
    "\xb8\x9e\x87\x02\x74\x92\x74\xd7\xff\x99\x15\x80" \
    "\x5e\xd2\x0d\xa2\xf9\xde\x0f\x19\xcd\x0b\xd1\xbc" \
    "\xe0\xfb\x3e\xbe\xe7\xe1\x15\x8b\x0c\x0d\x0d\xf5" \
    "\x99\x01\x54\xe7\x3b\xbf\xb2\xf5\x2e\x60\x49\x37" \
    "\xfa\x5a\xea\xe8\xaa\x19\xe0\x2f\xeb\xd0\xf5\x21" \
    "\x35\x3f\x01\x61\x00\x00\x00\x00\x49\x45\x4e\x44" \
    "\xae\x42\x60\x82"
image2_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x10\x00\x00\x00\x10" \
    "\x08\x06\x00\x00\x00\x1f\xf3\xff\x61\x00\x00\x02" \
    "\x79\x49\x44\x41\x54\x38\x8d\x6d\x93\xb1\x4b\x1b" \
    "\x61\x18\xc6\x7f\xdf\xdd\x77\x97\xe4\x50\xab\xd4" \
    "\x6a\xee\xaa\x71\x70\x50\x54\xaa\x24\xfe\x0d\x0e" \
    "\x6e\x0e\x82\x83\x50\x74\xb0\x52\x74\x73\xeb\xa0" \
    "\xe0\xe0\x1f\x10\x3a\x14\x5c\x32\xeb\xaa\x48\x0a" \
    "\x4d\xf7\x56\x74\xa8\xa8\x88\x83\x04\x15\xc5\xf3" \
    "\xaa\x46\x13\x2f\xb9\xbb\x0e\x97\xa8\x91\xbe\xf0" \
    "\xf0\xbd\xbc\x7c\xcf\xc3\xfb\xbe\x0f\xaf\x48\x26" \
    "\x93\xbc\x8c\x0c\xf4\x0a\x98\xf0\x00\x0f\xf0\x5f" \
    "\xbc\x7f\x61\xfd\x0b\xec\x01\x41\xed\xbf\x78\x29" \
    "\x90\x81\xde\x88\x61\xe4\xac\xf1\xf1\xb8\x50\xd5" \
    "\x3a\xe1\x8a\xe7\x71\xb0\xb6\x76\xf5\xe7\xe1\x61" \
    "\xf4\x2b\xfc\xae\x89\xc8\x3a\x72\x2c\x96\xeb\x5a" \
    "\x5c\x8c\xeb\xfd\xfd\xfc\x2f\x06\xfb\xfa\x5a\x2b" \
    "\x4b\x4b\x9b\x9f\x8a\xc5\xd1\x6f\x55\x11\xd5\x34" \
    "\xcd\x90\x1c\x89\xe4\xba\xe6\xe7\xe3\x7a\x67\x27" \
    "\xb8\x2e\xdc\xdc\x40\xa1\xf0\x8c\x52\x09\x19\x8d" \
    "\xf2\xae\xbb\xdb\x78\xdc\xde\x1e\xeb\xf0\xbc\xdc" \
    "\x0e\x9c\xab\x59\xd3\xec\x8d\xe8\x7a\xae\x6b\x72" \
    "\x32\xae\xb7\xb7\x43\x5b\x1b\xf4\xf4\x40\x3e\x0f" \
    "\x17\x17\x70\x77\x07\x91\x08\x0c\x0e\xc2\xed\x2d" \
    "\xf2\xfe\x9e\xb6\x44\xc2\x28\xed\xed\x8d\xbd\xf7" \
    "\xbc\x9c\x02\x4c\x58\x03\x03\x71\x5d\xd3\xe0\xf2" \
    "\x12\x12\x09\x50\x55\x48\xa5\x20\x08\x42\xa4\x52" \
    "\x61\x2d\x91\xc0\x3f\x3e\x46\x1e\x1d\xf1\xe1\xcd" \
    "\x9b\x56\x03\xa6\xa5\x07\x88\x42\x01\x4e\x4f\xc3" \
    "\x41\x57\x57\x61\x6a\x0a\x1a\x1b\x61\x64\x24\xac" \
    "\x49\x49\x60\xdb\x3c\xce\xcf\xe3\x1f\x1e\x86\xdb" \
    "\x07\x5c\xd0\x14\x1f\xe0\xf6\x36\x6c\x39\x9f\x87" \
    "\xdd\x5d\x58\x59\x09\x77\xa0\xeb\xa0\xeb\x04\xb6" \
    "\x4d\x69\x66\xe6\x89\x4c\xd5\x02\x1f\x90\x5e\x4d" \
    "\xc0\x75\x9f\xd7\xdd\xd2\x12\xce\x5d\x8b\x58\x0c" \
    "\xa5\xb9\x19\xef\x95\x2b\x3e\x10\x76\xf0\xf0\x40" \
    "\xe0\x38\x21\x12\x09\x58\x5e\x86\x68\x94\xc0\xb6" \
    "\x09\x6c\x1b\x61\x18\xe8\xe9\x34\xfa\xd0\x10\xb2" \
    "\xea\xbd\xac\x09\x78\x00\x8a\x02\x42\x40\x63\x23" \
    "\x22\x9d\x06\xc3\x80\xeb\x6b\x98\x9d\x0d\x71\x7d" \
    "\x8d\x30\x0c\x64\x3a\x8d\xd6\xd4\x84\xa6\x28\x04" \
    "\x8a\x12\x0a\xdc\xc0\xfa\x1e\x5c\x95\x1b\x1a\x10" \
    "\xaa\x0a\x99\x0c\x38\x0e\x2c\x2c\x20\x1c\x07\x51" \
    "\xcd\x71\x1c\xc8\x64\x10\xaa\x4a\xa9\xa1\x81\x9f" \
    "\xe0\xec\x43\x56\x24\x93\x49\xf1\x19\x86\xfb\x34" \
    "\x6d\x33\x65\x59\xad\xba\x94\x10\x8d\x42\xa9\x54" \
    "\x3f\x70\xb5\x56\xac\x54\xd8\x3a\x3b\x73\x36\xca" \
    "\xe5\xb9\x1d\xc8\xaa\xa6\x69\xf2\x0b\xce\x3b\x7c" \
    "\x3f\xe7\x3e\x3e\x8e\xc5\x2d\xcb\x90\xd1\x28\xc4" \
    "\x62\xf5\xd0\x34\x8a\xaa\xca\xd6\xc9\x89\xb3\xe1" \
    "\xba\x73\x3b\x90\x05\x6c\xd5\x34\x4d\x00\xb6\xe1" \
    "\xdc\xaa\x54\x72\xa5\x42\x61\xec\xad\x65\x19\x9e" \
    "\xae\x53\x96\x92\xb2\x94\xb8\x52\x52\x14\x82\xef" \
    "\xfb\xfb\xce\x46\xb1\xf8\x44\x06\x02\xf1\xea\x9c" \
    "\xc5\x47\x18\x36\x60\xda\x05\xcd\xaf\xfa\x5d\x3b" \
    "\xe7\x03\xc8\x6e\xc3\x8f\x1a\x19\xe0\x1f\x17\x26" \
    "\x01\xbe\xf9\x92\x50\x85\x00\x00\x00\x00\x49\x45" \
    "\x4e\x44\xae\x42\x60\x82"

class EDSMStateDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        self.image2 = QPixmap()
        self.image2.loadFromData(image2_data,"PNG")
        if not name:
            self.setName("EDSMStateDialog")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)

        EDSMStateDialogLayout = QGridLayout(self,1,1,11,6,"EDSMStateDialogLayout")

        self.object_name = QLineEdit(self,"object_name")

        EDSMStateDialogLayout.addWidget(self.object_name,0,1)

        self.object_name_textlabel = QLabel(self,"object_name_textlabel")

        EDSMStateDialogLayout.addWidget(self.object_name_textlabel,0,0)

        self.groupBox5 = QGroupBox(self,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        self.class_name = QComboBox(0,self.groupBox5,"class_name")
        self.class_name.setEditable(1)
        self.class_name.setInsertionPolicy(QComboBox.NoInsertion)
        self.class_name.setAutoCompletion(1)
        self.class_name.setDuplicatesEnabled(0)

        groupBox5Layout.addWidget(self.class_name,0,1)

        self.language_name = QComboBox(0,self.groupBox5,"language_name")

        groupBox5Layout.addWidget(self.language_name,1,1)

        self.init_code = QTextEdit(self.groupBox5,"init_code")
        init_code_font = QFont(self.init_code.font())
        init_code_font.setFamily("Monospace")
        init_code_font.setPointSize(8)
        self.init_code.setFont(init_code_font)

        groupBox5Layout.addWidget(self.init_code,2,1)

        self.class_name_textlabel = QLabel(self.groupBox5,"class_name_textlabel")

        groupBox5Layout.addWidget(self.class_name_textlabel,0,0)

        self.language_name_textlabel = QLabel(self.groupBox5,"language_name_textlabel")

        groupBox5Layout.addWidget(self.language_name_textlabel,1,0)

        self.init_code_textlabel = QLabel(self.groupBox5,"init_code_textlabel")

        groupBox5Layout.addWidget(self.init_code_textlabel,2,0)

        EDSMStateDialogLayout.addMultiCellWidget(self.groupBox5,2,2,0,1)

        self.groupBox4 = QGroupBox(self,"groupBox4")
        self.groupBox4.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.groupBox4.sizePolicy().hasHeightForWidth()))
        self.groupBox4.setColumnLayout(0,Qt.Vertical)
        self.groupBox4.layout().setSpacing(6)
        self.groupBox4.layout().setMargin(11)
        groupBox4Layout = QGridLayout(self.groupBox4.layout())
        groupBox4Layout.setAlignment(Qt.AlignTop)

        self.output_queues = QListBox(self.groupBox4,"output_queues")

        groupBox4Layout.addWidget(self.output_queues,1,1)

        self.output_queues_textlabel = QFrame(self.groupBox4,"output_queues_textlabel")
        self.output_queues_textlabel.setFrameShape(QFrame.StyledPanel)
        self.output_queues_textlabel.setFrameShadow(QFrame.Raised)
        self.output_queues_textlabel.setLineWidth(0)
        output_queues_textlabelLayout = QGridLayout(self.output_queues_textlabel,1,1,0,3,"output_queues_textlabelLayout")

        self.add_output_queue_button = QPushButton(self.output_queues_textlabel,"add_output_queue_button")
        self.add_output_queue_button.setEnabled(0)
        self.add_output_queue_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.add_output_queue_button.sizePolicy().hasHeightForWidth()))
        self.add_output_queue_button.setPixmap(self.image1)

        output_queues_textlabelLayout.addWidget(self.add_output_queue_button,0,1)

        self.remove_output_queue_button = QPushButton(self.output_queues_textlabel,"remove_output_queue_button")
        self.remove_output_queue_button.setEnabled(0)
        self.remove_output_queue_button.setPixmap(self.image2)

        output_queues_textlabelLayout.addWidget(self.remove_output_queue_button,1,1)

        self.output_queues_label = QLabel(self.output_queues_textlabel,"output_queues_label")
        self.output_queues_label.setLineWidth(0)
        self.output_queues_label.setMargin(0)

        output_queues_textlabelLayout.addMultiCellWidget(self.output_queues_label,0,1,0,0)

        groupBox4Layout.addWidget(self.output_queues_textlabel,1,0)

        self.input_queues_textlabel = QFrame(self.groupBox4,"input_queues_textlabel")
        self.input_queues_textlabel.setFrameShape(QFrame.StyledPanel)
        self.input_queues_textlabel.setFrameShadow(QFrame.Raised)
        self.input_queues_textlabel.setLineWidth(0)
        input_queues_textlabelLayout = QGridLayout(self.input_queues_textlabel,1,1,0,3,"input_queues_textlabelLayout")

        self.add_input_queue_button = QPushButton(self.input_queues_textlabel,"add_input_queue_button")
        self.add_input_queue_button.setEnabled(0)
        self.add_input_queue_button.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.add_input_queue_button.sizePolicy().hasHeightForWidth()))
        self.add_input_queue_button.setPixmap(self.image1)

        input_queues_textlabelLayout.addWidget(self.add_input_queue_button,0,1)

        self.remove_input_queue_button = QPushButton(self.input_queues_textlabel,"remove_input_queue_button")
        self.remove_input_queue_button.setEnabled(0)
        self.remove_input_queue_button.setPixmap(self.image2)

        input_queues_textlabelLayout.addWidget(self.remove_input_queue_button,1,1)

        self.input_queues_label = QLabel(self.input_queues_textlabel,"input_queues_label")
        self.input_queues_label.setLineWidth(0)
        self.input_queues_label.setMargin(0)

        input_queues_textlabelLayout.addMultiCellWidget(self.input_queues_label,0,1,0,0)

        groupBox4Layout.addWidget(self.input_queues_textlabel,1,2)

        self.input_queues = QListBox(self.groupBox4,"input_queues")

        groupBox4Layout.addWidget(self.input_queues,1,3)

        self.queue_name = QLineEdit(self.groupBox4,"queue_name")

        groupBox4Layout.addMultiCellWidget(self.queue_name,0,0,1,3)

        self.queue_name_textlabel = QLabel(self.groupBox4,"queue_name_textlabel")

        groupBox4Layout.addWidget(self.queue_name_textlabel,0,0)

        EDSMStateDialogLayout.addMultiCellWidget(self.groupBox4,1,1,0,1)

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

        EDSMStateDialogLayout.addMultiCellLayout(Layout1,3,3,0,1)

        self.languageChange()

        self.resize(QSize(382,340).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.buttonOk,SIGNAL("clicked()"),self.accept)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self.reject)
        self.connect(self.language_name,SIGNAL("activated(const QString&)"),self.language_name_activated)
        self.connect(self.output_queues,SIGNAL("selectionChanged()"),self.output_queues_selectionChanged)
        self.connect(self.input_queues,SIGNAL("selectionChanged()"),self.input_queues_selectionChanged)
        self.connect(self.queue_name,SIGNAL("textChanged(const QString&)"),self.queue_name_textChanged)
        self.connect(self.add_input_queue_button,SIGNAL("clicked()"),self.add_input_queue_button_clicked)
        self.connect(self.add_output_queue_button,SIGNAL("clicked()"),self.add_output_queue_button_clicked)
        self.connect(self.remove_input_queue_button,SIGNAL("clicked()"),self.remove_input_queue_button_clicked)
        self.connect(self.remove_output_queue_button,SIGNAL("clicked()"),self.remove_output_queue_button_clicked)

        self.setTabOrder(self.object_name,self.class_name)
        self.setTabOrder(self.class_name,self.init_code)
        self.setTabOrder(self.init_code,self.buttonOk)
        self.setTabOrder(self.buttonOk,self.buttonCancel)
        self.setTabOrder(self.buttonCancel,self.buttonHelp)

        self.object_name_textlabel.setBuddy(self.object_name)
        self.init_code_textlabel.setBuddy(self.init_code)
        self.queue_name_textlabel.setBuddy(self.object_name)


    def languageChange(self):
        self.setCaption(self.__tr("EDSM State Dialog"))
        self.object_name_textlabel.setText(self.__tr("Name:"))
        self.groupBox5.setTitle(self.__tr("Implementation"))
        self.language_name.clear()
        self.language_name.insertItem(self.__tr("Python"))
        self.class_name_textlabel.setText(self.__tr("Class:"))
        self.language_name_textlabel.setText(self.__tr("Language:"))
        self.init_code_textlabel.setText(self.__tr("Init code:"))
        self.groupBox4.setTitle(self.__tr("Queues"))
        self.add_output_queue_button.setText(QString.null)
        QToolTip.add(self.add_output_queue_button,self.__tr("Apply"))
        self.remove_output_queue_button.setText(QString.null)
        self.output_queues_label.setText(self.__tr("Output"))
        self.add_input_queue_button.setText(QString.null)
        QToolTip.add(self.add_input_queue_button,self.__tr("Apply"))
        self.remove_input_queue_button.setText(QString.null)
        self.input_queues_label.setText(self.__tr("Input"))
        self.queue_name_textlabel.setText(self.__tr("New Queue"))
        self.buttonHelp.setText(self.__tr("&Help"))
        self.buttonHelp.setAccel(self.__tr("F1"))
        self.buttonOk.setText(self.__tr("&OK"))
        self.buttonOk.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("&Cancel"))
        self.buttonCancel.setAccel(QString.null)


    def language_name_activated(self,a0):
        print "EDSMStateDialog.language_name_activated(const QString&): Not implemented yet"

    def output_queues_selectionChanged(self):
        print "EDSMStateDialog.output_queues_selectionChanged(): Not implemented yet"

    def input_queues_selectionChanged(self):
        print "EDSMStateDialog.input_queues_selectionChanged(): Not implemented yet"

    def queue_name_textChanged(self,a0):
        print "EDSMStateDialog.queue_name_textChanged(const QString&): Not implemented yet"

    def add_input_queue_button_clicked(self):
        print "EDSMStateDialog.add_input_queue_button_clicked(): Not implemented yet"

    def add_output_queue_button_clicked(self):
        print "EDSMStateDialog.add_output_queue_button_clicked(): Not implemented yet"

    def remove_input_queue_button_clicked(self):
        print "EDSMStateDialog.remove_input_queue_button_clicked(): Not implemented yet"

    def remove_output_queue_button_clicked(self):
        print "EDSMStateDialog.remove_output_queue_button_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("EDSMStateDialog",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = EDSMStateDialog()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
