# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qctlib/dialog.ui'
#
# Created: Fri Jan 19 22:21:14 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_commitToolDialog(object):
    def setupUi(self, commitToolDialog):
        commitToolDialog.setObjectName("commitToolDialog")
        commitToolDialog.resize(QtCore.QSize(QtCore.QRect(0,0,672,675).size()).expandedTo(commitToolDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(commitToolDialog.sizePolicy().hasHeightForWidth())
        commitToolDialog.setSizePolicy(sizePolicy)
        commitToolDialog.setMinimumSize(QtCore.QSize(672,0))

        self.vboxlayout = QtGui.QVBoxLayout(commitToolDialog)
        self.vboxlayout.setMargin(9)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.commitMsgBox = QtGui.QGroupBox(commitToolDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commitMsgBox.sizePolicy().hasHeightForWidth())
        self.commitMsgBox.setSizePolicy(sizePolicy)
        self.commitMsgBox.setMinimumSize(QtCore.QSize(0,132))
        self.commitMsgBox.setMaximumSize(QtCore.QSize(16777215,123))
        self.commitMsgBox.setObjectName("commitMsgBox")

        self.hboxlayout = QtGui.QHBoxLayout(self.commitMsgBox)
        self.hboxlayout.setMargin(9)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.commitTextEntry = QtGui.QTextEdit(self.commitMsgBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commitTextEntry.sizePolicy().hasHeightForWidth())
        self.commitTextEntry.setSizePolicy(sizePolicy)
        self.commitTextEntry.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.commitTextEntry.setTabChangesFocus(True)
        self.commitTextEntry.setAcceptRichText(False)
        self.commitTextEntry.setObjectName("commitTextEntry")
        self.vboxlayout1.addWidget(self.commitTextEntry)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.label = QtGui.QLabel(self.commitMsgBox)
        self.label.setObjectName("label")
        self.hboxlayout1.addWidget(self.label)

        self.logHistComboBox = QtGui.QComboBox(self.commitMsgBox)
        self.logHistComboBox.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.logHistComboBox.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.logHistComboBox.setObjectName("logHistComboBox")
        self.hboxlayout1.addWidget(self.logHistComboBox)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout1)
        self.hboxlayout.addLayout(self.vboxlayout1)
        self.vboxlayout.addWidget(self.commitMsgBox)

        self.splitter = QtGui.QSplitter(commitToolDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")

        self.fileListBox = QtGui.QGroupBox(self.splitter)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileListBox.sizePolicy().hasHeightForWidth())
        self.fileListBox.setSizePolicy(sizePolicy)
        self.fileListBox.setMinimumSize(QtCore.QSize(0,0))
        self.fileListBox.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.fileListBox.setObjectName("fileListBox")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.fileListBox)
        self.vboxlayout2.setMargin(9)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.selectAllPushButton = QtGui.QPushButton(self.fileListBox)
        self.selectAllPushButton.setObjectName("selectAllPushButton")
        self.hboxlayout2.addWidget(self.selectAllPushButton)

        self.refreshPushButton = QtGui.QPushButton(self.fileListBox)
        self.refreshPushButton.setObjectName("refreshPushButton")
        self.hboxlayout2.addWidget(self.refreshPushButton)

        spacerItem1 = QtGui.QSpacerItem(191,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)

        self.prefPushButton = QtGui.QPushButton(self.fileListBox)
        self.prefPushButton.setObjectName("prefPushButton")
        self.hboxlayout2.addWidget(self.prefPushButton)
        self.vboxlayout2.addLayout(self.hboxlayout2)

        self.fileListWidget = QtGui.QListWidget(self.fileListBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileListWidget.sizePolicy().hasHeightForWidth())
        self.fileListWidget.setSizePolicy(sizePolicy)
        self.fileListWidget.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.fileListWidget.setAutoFillBackground(True)
        self.fileListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.fileListWidget.setAlternatingRowColors(True)
        self.fileListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.fileListWidget.setWrapping(False)
        self.fileListWidget.setResizeMode(QtGui.QListView.Adjust)
        self.fileListWidget.setSpacing(2)
        self.fileListWidget.setObjectName("fileListWidget")
        self.vboxlayout2.addWidget(self.fileListWidget)

        self.diffBrowserBox = QtGui.QGroupBox(self.splitter)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.diffBrowserBox.sizePolicy().hasHeightForWidth())
        self.diffBrowserBox.setSizePolicy(sizePolicy)
        self.diffBrowserBox.setObjectName("diffBrowserBox")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.diffBrowserBox)
        self.vboxlayout3.setMargin(9)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.diffBrowser = QtGui.QTextEdit(self.diffBrowserBox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.diffBrowser.sizePolicy().hasHeightForWidth())
        self.diffBrowser.setSizePolicy(sizePolicy)
        self.diffBrowser.setMinimumSize(QtCore.QSize(0,0))
        self.diffBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.diffBrowser.setAcceptDrops(False)
        self.diffBrowser.setObjectName("diffBrowser")
        self.vboxlayout3.addWidget(self.diffBrowser)
        self.vboxlayout.addWidget(self.splitter)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem2 = QtGui.QSpacerItem(75,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem2)

        self.commitPushButton = QtGui.QPushButton(commitToolDialog)
        self.commitPushButton.setObjectName("commitPushButton")
        self.hboxlayout3.addWidget(self.commitPushButton)

        self.cancelPushButton = QtGui.QPushButton(commitToolDialog)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.hboxlayout3.addWidget(self.cancelPushButton)
        self.vboxlayout.addLayout(self.hboxlayout3)
        self.label.setBuddy(self.logHistComboBox)

        self.retranslateUi(commitToolDialog)
        QtCore.QObject.connect(self.cancelPushButton,QtCore.SIGNAL("pressed()"),commitToolDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(commitToolDialog)
        commitToolDialog.setTabOrder(self.commitTextEntry,self.fileListWidget)
        commitToolDialog.setTabOrder(self.fileListWidget,self.commitPushButton)
        commitToolDialog.setTabOrder(self.commitPushButton,self.cancelPushButton)
        commitToolDialog.setTabOrder(self.cancelPushButton,self.logHistComboBox)
        commitToolDialog.setTabOrder(self.logHistComboBox,self.selectAllPushButton)
        commitToolDialog.setTabOrder(self.selectAllPushButton,self.refreshPushButton)

    def retranslateUi(self, commitToolDialog):
        commitToolDialog.setWindowTitle(QtGui.QApplication.translate("commitToolDialog", "Commit Tool", None, QtGui.QApplication.UnicodeUTF8))
        self.commitMsgBox.setTitle(QtGui.QApplication.translate("commitToolDialog", "Commit Message", None, QtGui.QApplication.UnicodeUTF8))
        self.commitTextEntry.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Here you enter a log message describing the changes made to the selected files.  There are several useful keyboard shortcuts:</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CTRL-N - display next file</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CTRL-[  - page up file changes</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CTRL-]  - page down file changes</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CTRL-O - commit</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">ESC  - abort</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.commitTextEntry.setHtml(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("commitToolDialog", "Most Recent:", None, QtGui.QApplication.UnicodeUTF8))
        self.logHistComboBox.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This combo box allows you to select one of your most recent commit messages.  The selected message is copied into the commit message text area, overwriting any text that was already there.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.fileListBox.setTitle(QtGui.QApplication.translate("commitToolDialog", "File List", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllPushButton.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This button will attempt to select (check) every file in the file list.  If all of the files were already selected, it will unselect them all instead.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.selectAllPushButton.setText(QtGui.QApplication.translate("commitToolDialog", "(Un)Select All", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshPushButton.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This button causes the revision control system to re-inspect the state of the repository.  This should only be necessary if you have modified the repository since this dialog was opened.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshPushButton.setText(QtGui.QApplication.translate("commitToolDialog", "&Refresh List", None, QtGui.QApplication.UnicodeUTF8))
        self.prefPushButton.setText(QtGui.QApplication.translate("commitToolDialog", "Preferences ...", None, QtGui.QApplication.UnicodeUTF8))
        self.fileListWidget.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This is the list of commitable files.  Files which are checked will be commited together as a group when the commit button (or CTRL-O) is pressed.  The revert button will also limit it\'s operation to the list of checked files.</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">At startup, and after each commit, Qct will automatically preselect all the commitable files which are already revisioned.  This is for your convenience, since in most cases you will want to commit these files together as a group.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.diffBrowserBox.setTitle(QtGui.QApplication.translate("commitToolDialog", "File Changes", None, QtGui.QApplication.UnicodeUTF8))
        self.diffBrowser.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This window will display the changes (diffs/deltas) made to the file currently selected in the file list.  These are useful for providing meaningful commit messages.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.diffBrowser.setHtml(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.commitPushButton.setToolTip(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Commit selected (checked) files</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.commitPushButton.setWhatsThis(QtGui.QApplication.translate("commitToolDialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Commit the selected (checked) files using the commit log message you provide in the top text area.  Some VCS tools refer to this function as a submit, others a check-in.</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If, after commiting the selected files, no commitable files remain in your repository, Qct will automatically exit.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.commitPushButton.setText(QtGui.QApplication.translate("commitToolDialog", "C&ommit", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("commitToolDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

