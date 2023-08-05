# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qctlib/preferences.ui'
#
# Created: Fri Jan 19 22:21:14 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_prefDialog(object):
    def setupUi(self, prefDialog):
        prefDialog.setObjectName("prefDialog")
        prefDialog.resize(QtCore.QSize(QtCore.QRect(0,0,314,307).size()).expandedTo(prefDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(prefDialog.sizePolicy().hasHeightForWidth())
        prefDialog.setSizePolicy(sizePolicy)
        prefDialog.setModal(True)

        self.groupBox_2 = QtGui.QGroupBox(prefDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10,0,291,201))
        self.groupBox_2.setObjectName("groupBox_2")

        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(10,80,54,16))
        self.label_2.setObjectName("label_2")

        self.editToolEdit = QtGui.QLineEdit(self.groupBox_2)
        self.editToolEdit.setGeometry(QtCore.QRect(10,100,191,24))
        self.editToolEdit.setObjectName("editToolEdit")

        self.editToolBrowseButton = QtGui.QPushButton(self.groupBox_2)
        self.editToolBrowseButton.setGeometry(QtCore.QRect(210,100,75,26))
        self.editToolBrowseButton.setObjectName("editToolBrowseButton")

        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setGeometry(QtCore.QRect(10,20,71,16))
        self.label.setObjectName("label")

        self.diffToolBrowseButton = QtGui.QPushButton(self.groupBox_2)
        self.diffToolBrowseButton.setGeometry(QtCore.QRect(210,40,75,26))
        self.diffToolBrowseButton.setObjectName("diffToolBrowseButton")

        self.diffToolEdit = QtGui.QLineEdit(self.groupBox_2)
        self.diffToolEdit.setGeometry(QtCore.QRect(10,40,191,24))
        self.diffToolEdit.setObjectName("diffToolEdit")

        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(10,140,101,16))
        self.label_3.setObjectName("label_3")

        self.mergeToolEdit = QtGui.QLineEdit(self.groupBox_2)
        self.mergeToolEdit.setGeometry(QtCore.QRect(10,160,191,24))
        self.mergeToolEdit.setObjectName("mergeToolEdit")

        self.mergeToolBrowseButton = QtGui.QPushButton(self.groupBox_2)
        self.mergeToolBrowseButton.setGeometry(QtCore.QRect(210,160,75,26))
        self.mergeToolBrowseButton.setObjectName("mergeToolBrowseButton")

        self.groupBox = QtGui.QGroupBox(prefDialog)
        self.groupBox.setGeometry(QtCore.QRect(10,210,122,86))
        self.groupBox.setObjectName("groupBox")

        self.vboxlayout = QtGui.QVBoxLayout(self.groupBox)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.wrapListCheckBox = QtGui.QCheckBox(self.groupBox)
        self.wrapListCheckBox.setObjectName("wrapListCheckBox")
        self.vboxlayout.addWidget(self.wrapListCheckBox)

        self.ignoredButton = QtGui.QCheckBox(self.groupBox)
        self.ignoredButton.setObjectName("ignoredButton")
        self.vboxlayout.addWidget(self.ignoredButton)

        self.pushButton_2 = QtGui.QPushButton(prefDialog)
        self.pushButton_2.setGeometry(QtCore.QRect(230,270,75,24))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton = QtGui.QPushButton(prefDialog)
        self.pushButton.setGeometry(QtCore.QRect(150,270,75,24))
        self.pushButton.setObjectName("pushButton")
        self.label_2.setBuddy(self.editToolEdit)
        self.label.setBuddy(self.diffToolEdit)
        self.label_3.setBuddy(self.mergeToolEdit)

        self.retranslateUi(prefDialog)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),prefDialog.accept)
        QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),prefDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(prefDialog)
        prefDialog.setTabOrder(self.diffToolEdit,self.diffToolBrowseButton)
        prefDialog.setTabOrder(self.diffToolBrowseButton,self.editToolEdit)
        prefDialog.setTabOrder(self.editToolEdit,self.editToolBrowseButton)
        prefDialog.setTabOrder(self.editToolBrowseButton,self.mergeToolEdit)
        prefDialog.setTabOrder(self.mergeToolEdit,self.mergeToolBrowseButton)
        prefDialog.setTabOrder(self.mergeToolBrowseButton,self.wrapListCheckBox)
        prefDialog.setTabOrder(self.wrapListCheckBox,self.ignoredButton)

    def retranslateUi(self, prefDialog):
        prefDialog.setWindowTitle(QtGui.QApplication.translate("prefDialog", "Qct Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("prefDialog", "External Applications", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setToolTip(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Supply the name of an external editor, it will be offered as an option in the context menu of appropriate files.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("prefDialog", "Editor:", None, QtGui.QApplication.UnicodeUTF8))
        self.editToolBrowseButton.setText(QtGui.QApplication.translate("prefDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setToolTip(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Specify an alternative diff browser which is supported by your revision control tool.  It will be passed the name of the file you wish to browse, so the VCS must supply the actual diffs.  Example: hg vdiff</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("prefDialog", "Diff Viewer:", None, QtGui.QApplication.UnicodeUTF8))
        self.diffToolBrowseButton.setText(QtGui.QApplication.translate("prefDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setToolTip(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Specify a two-way merge program that can be used to select changes in your working files for commit.   Examples: Kompare, meld, and kdiff3 are possibilities.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("prefDialog", "Two-Way Merge:", None, QtGui.QApplication.UnicodeUTF8))
        self.mergeToolBrowseButton.setText(QtGui.QApplication.translate("prefDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("prefDialog", "File List", None, QtGui.QApplication.UnicodeUTF8))
        self.wrapListCheckBox.setToolTip(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Flow file names from left to right with wrapping</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.wrapListCheckBox.setWhatsThis(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This toggles the layout of the file list.  If checked, the files will flow from left to right with wrapping at the right edge and scrolling at the bottom edge.  If unchecked, the files will be in a single row from top to bottom.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.wrapListCheckBox.setText(QtGui.QApplication.translate("prefDialog", "Wrap List", None, QtGui.QApplication.UnicodeUTF8))
        self.ignoredButton.setToolTip(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Show files normally ignored by revision control</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.ignoredButton.setWhatsThis(QtGui.QApplication.translate("prefDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This button toggles display of unrevisioned files which are typically ignored by your revision control system (via ignore masks).  If you commit one of these files it will be automatically added to revision control.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.ignoredButton.setText(QtGui.QApplication.translate("prefDialog", "Show Ignored", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("prefDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("prefDialog", "Ok", None, QtGui.QApplication.UnicodeUTF8))

