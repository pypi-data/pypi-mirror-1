# dialogLogic.py - Commit Tool
#
# Copyright 2006 Steve Borho
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

from PyQt4 import QtCore, QtGui
from qctlib.ui_dialog import Ui_commitToolDialog
from qctlib.ui_preferences import Ui_prefDialog
from qctlib.utils import formatPatchRichText, runProgram
import os, sys, shutil

class CommitTool(QtGui.QWidget):
    '''QCT commit tool GUI logic'''
    def __init__(self, vcs):
        '''Initialize the dialog window, fill with initial data'''
        QtGui.QWidget.__init__(self)

        self.maxHistCount = 8
        self.vcs = vcs
        self.autoSelectTypes = self.vcs.getAutoSelectTypes()
        self.patchColors = {'std': 'black', 'new': '#009600', 'remove': '#C80000', 'head': '#C800C8'}
        self.fileCheckState = {}
        self.logHistory = []
        self.changeSelectedFiles = []
        self.showIgnored = False
        self.wrapList = False
        self.itemChangeEntered = False
        self.logTemplate = None

        self.ui = Ui_commitToolDialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowContextHelpButtonHint)

        # Support for Mercurial Queues, and Stacked Git.  If a patch is
        # applied, then the user is refreshing that patch, not commiting
        # to the underlying repository.
        self.patchRefreshMode = False
        self.commitButtonToolTip = "Commit selected (checked) files"
        if 'patchqueue' in self.vcs.capabilities() and self.vcs.isPatchQueue():
            self.patchRefreshMode = True
            self.ui.commitMsgBox.setTitle(QtGui.QApplication.translate("commitToolDialog",
                "Patch Description: " + self.vcs.topPatchName(),
                None, QtGui.QApplication.UnicodeUTF8))
            self.ui.commitTextEntry.setToolTip(QtGui.QApplication.translate("commitToolDialog",
                "Description of current top patch " + self.vcs.topPatchName(),
                None, QtGui.QApplication.UnicodeUTF8))
            self.ui.commitPushButton.setText(QtGui.QApplication.translate("commitToolDialog",
                "Refresh Patch", None, QtGui.QApplication.UnicodeUTF8))
            self.commitButtonToolTip = "Refresh selected files in patch " + self.vcs.topPatchName()

        # Recover persistent data
        settings = QtCore.QSettings('vcs', 'qct')
        settings.beginGroup('mainwindow')
        if settings.contains('size'):
            self.resize(settings.value('size').toSize())
            self.move(settings.value('pos').toPoint())
            self.ui.splitter.restoreState(settings.value('splitter').toByteArray())
        settings.endGroup()
        settings.beginGroup('commitLog')
        size = settings.beginReadArray('history')
        for i in xrange(0, size):
            settings.setArrayIndex(i)
            self.logHistory.append(settings.value('text').toString())
        settings.endArray()
        settings.endGroup()

        self.connect(self.ui.fileListWidget,
                QtCore.SIGNAL("customContextMenuRequested(const QPoint &)"),
                self.__contextMenu)

        self.__fillLogHistCombo()

        # Prepare for simple syntax highlighting
        self.ui.diffBrowser.setAcceptRichText(True)

        # Setup ESC to exit
        self.actionEsc = QtGui.QAction(self)
        self.actionEsc.setShortcut(QtGui.QKeySequence(self.tr("ESC")))
        self.ui.commitTextEntry.addAction(self.actionEsc)
        self.connect(self.actionEsc, QtCore.SIGNAL("triggered()"), self.close)

        # Setup CTRL-O to trigger commit
        self.actionCtrlO = QtGui.QAction(self)
        self.actionCtrlO.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+O")))
        self.ui.commitTextEntry.addAction(self.actionCtrlO)
        self.connect(self.actionCtrlO, QtCore.SIGNAL("triggered()"), self.commitSelected)

        # Setup CTRL-R to trigger refresh
        self.actionCtrlR = QtGui.QAction(self)
        self.actionCtrlR.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+R")))
        self.ui.commitTextEntry.addAction(self.actionCtrlR)
        self.connect(self.actionCtrlR, QtCore.SIGNAL("triggered()"), self.on_refreshPushButton_pressed)

        # Setup CTRL-N to display next file
        self.actionCtrlN = QtGui.QAction(self)
        self.actionCtrlN.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+N")))
        self.ui.commitTextEntry.addAction(self.actionCtrlN)
        self.connect(self.actionCtrlN, QtCore.SIGNAL("triggered()"), self.displayNextFile)

        # Setup CTRL-U to select next file
        self.actionCtrlU = QtGui.QAction(self)
        self.actionCtrlU.setShortcut(QtGui.QKeySequence(self.tr("Ctrl+U")))
        self.ui.commitTextEntry.addAction(self.actionCtrlU)
        self.connect(self.actionCtrlU, QtCore.SIGNAL("triggered()"), self.unselectAll)

        # Setup CTRL-] to scroll browser window
        self.actionPageDown = QtGui.QAction(self)
        self.actionPageDown.setShortcut(QtGui.QKeySequence(self.tr("CTRL+]")))
        self.ui.commitTextEntry.addAction(self.actionPageDown)
        self.connect(self.actionPageDown, QtCore.SIGNAL("triggered()"), self.__pageDownBrowser)

        # Setup CTRL-[ to scroll browser window
        self.actionPageUp = QtGui.QAction(self)
        self.actionPageUp.setShortcut(QtGui.QKeySequence(self.tr("CTRL+[")))
        self.ui.commitTextEntry.addAction(self.actionPageUp)
        self.connect(self.actionPageUp, QtCore.SIGNAL("triggered()"), self.__pageUpBrowser)

        self.connect(self.ui.commitPushButton, QtCore.SIGNAL("clicked()"), self.commitSelected)
        self.ui.fileListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.__retrieveConfigurables()
        self.__rescanFiles()
        if not self.itemList:
            print "No uncommited changes"
            sys.exit()
            return
        self.__refreshFileList(True)
        self.__updateCommitButtonState()

    def reject(self):
        '''User has pushed the cancel button'''
        self.close()

    def __retrieveConfigurables(self):
        '''Run at startup and after the preferences dialog exits'''
        settings = QtCore.QSettings('vcs', 'qct')
        settings.beginGroup('fileList')
        self.showIgnored = settings.value('showIgnored', QtCore.QVariant(False)).toBool()
        self.wrapList = settings.value('wrapping', QtCore.QVariant(False)).toBool()
        settings.endGroup()

        settings.beginGroup('tools')
        self.diffTool = str(settings.value('diffTool', QtCore.QVariant('')).toString())
        self.editTool = str(settings.value('editTool', QtCore.QVariant('')).toString())
        self.twowayTool = str(settings.value('twowayTool', QtCore.QVariant('')).toString())
        settings.endGroup()

        # Disable the 'show ignored' feature if VCS does not support it (perforce)
        if 'ignore' not in self.vcs.capabilities():
            self.showIgnored = False

        if self.wrapList:
            self.ui.fileListWidget.setWrapping( True )
            self.ui.fileListWidget.setFlow( QtGui.QListView.LeftToRight )
            # self.ui.fileListWidget.setUniformItemSizes( True )
        else:
            self.ui.fileListWidget.setWrapping( False )
            self.ui.fileListWidget.setFlow( QtGui.QListView.TopToBottom )
            # self.ui.fileListWidget.setUniformItemSizes( False )

    def __rescanFiles(self):
        '''Helper function which wraps progress bar functionality around
           the call to vcs.scanFiles()
        '''
        if 'progressbar' in self.vcs.capabilities():
            pb = QtGui.QProgressDialog()
            pb.setWindowTitle('Repository Scan')
            pb.setLabelText('Progress of repository scan')
            pb.setMinimum(0)
            pb.setMaximum(4)
            pb.setModal(True)
            pb.forceShow()
            pb.setValue(0)
            self.itemList = self.vcs.scanFiles(self.showIgnored, pb)
        else:
            self.itemList = self.vcs.scanFiles(self.showIgnored)

    def __contextMenu(self, Point):
        '''User has right clicked inside the file list window
           (or pressed the windows menu key).  We determine which
           item is under the mouse and then present options.
        '''
        item = self.ui.fileListWidget.itemAt(Point)
        if not item: return
        menuPos = self.ui.fileListWidget.mapToGlobal(Point)

        # Multi-selection context menu
        selectedItemList = self.ui.fileListWidget.selectedItems()
        if len(selectedItemList) > 1:
            allUnknowns = True
            for item in selectedItemList:
                itemName = str(item.text())
                if itemName[0] not in ['?', 'I']:
                    allUnknowns = False
                    break
            if allUnknowns:
                menu = QtGui.QMenu()
                menu.addAction("Delete all selected files")
                a = menu.exec_(menuPos)
                if a is not None:
                    if QtGui.QMessageBox.warning(self, "File Deletion Warning",
                            "Are you sure you want to delete all selected files?",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) != QtGui.QMessageBox.Ok:
                        return
                    for item in selectedItemList:
                        itemName = str(item.text())
                        if os.path.isdir(itemName[2:]):
                            shutil.rmtree(itemName[2:])
                        else:
                            os.unlink(itemName[2:])
                return
            else:
                menu = QtGui.QMenu()
                menu.addAction("Revert all selected files")
                if self.diffTool:
                    menu.addAction("Visual diff")
                    if self.patchRefreshMode:
                        menu.addAction("Visual diff of all patch changes")
                a = menu.exec_(menuPos)
                if not a: return
                actionText = str(a.text())
                if actionText.startswith('Revert'):
                    if QtGui.QMessageBox.warning(self, "Revert Warning",
                            "Are you sure you want to revert all selected files?",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) != QtGui.QMessageBox.Ok:
                        return
                    fileList = []
                    for item in selectedItemList:
                        itemName = str(item.text())
                        fileList.append(itemName)
                    self.vcs.revertFiles(fileList)
                    self.__rescanFiles()
                    self.__refreshFileList(False)
                if actionText.startswith('Visual diff'):
                    fileList = []
                    # Hack to get visual diff of all changes in the patch, not
                    # just those in the working directory
                    if actionText.endswith('all patch changes'): fileList = ['--rev', '-2' ]
                    for item in selectedItemList:
                        itemName = str(item.text())
                        fileList.append(itemName[2:])
                    runProgram(self.diffTool.split(' ') + fileList, expectedexits=[0,1,255])
                    self.__rescanFiles()
                    self.__refreshFileList(False)
                return

        itemName = str(item.text())
        targetType = itemName[0]
        targetFile = itemName[2:]

        # Context menu for unknown files (ignore masks or copy detection)
        if targetType in ['?', 'I']:
            menu = QtGui.QMenu()
            if targetType == '?' and 'ignore' in self.vcs.capabilities():
                basename = os.path.basename(targetFile) # baz.ext
                dirname = os.path.dirname(targetFile)   # foo/bar else ''
                ext = os.path.splitext(basename)[1]     # .ext else ''
                menu.addAction("Add Ignore: %s" % targetFile)
                if dirname and ext: menu.addAction("Add Ignore: %s/*%s" % (dirname, ext))
                if dirname:         menu.addAction("Add Ignore: %s" % basename)
                if ext:             menu.addAction("Add Ignore: *%s" % ext)
            if 'copy' in self.vcs.capabilities():
                menu.addAction("%s is a copy of a revisioned file" % targetFile)
            if self.editTool:
                menu.addAction("Open in %s" % os.path.basename(self.editTool))
            menu.addAction("Delete %s" % targetFile)
            a = menu.exec_(menuPos)
            if a is not None:
                actionText = str(a.text())
                if actionText.startswith('Add Ignore: '):
                    self.vcs.addIgnoreMask(actionText[12:])
                elif actionText.startswith('Open '):
                    runProgram([self.editTool, targetFile], expectedexits=[0,1,255])
                    self.vcs.dirtyCache(targetFile)
                    self.__refreshFileList(False)
                elif actionText.startswith('Delete '):
                    if QtGui.QMessageBox.warning(self, "File Deletion Warning",
                            "Are you sure you want to delete %s?" % targetFile,
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) != QtGui.QMessageBox.Ok:
                        return
                    if os.path.isdir(targetFile):
                        shutil.rmtree(targetFile)
                    else:
                        os.unlink(targetFile)
                else:
                    self.__detectFileCopySource(targetFile)
                self.__rescanFiles()
                self.__refreshFileList(False)

        # Context menu for rename events
        if targetType == '>':
            menu = QtGui.QMenu()
            menu.addAction("Revert rename back to %s" % targetFile)
            a = menu.exec_(menuPos)
            if not a: return
            self.__revertFile(itemName)
            self.__rescanFiles()
            self.__refreshFileList(False)
            return

        # Context menu for missing files (detect renames)
        if targetType == '!':
            menu = QtGui.QMenu()

            # Present unknown files as possible rename/move targets
            if self.unknownFileList and 'rename' in self.vcs.capabilities():
                for u in self.unknownFileList:
                    menu.addAction("%s was moved/renamed to %s" % (targetFile, u))
            menu.addAction("Recover %s from revision control" % targetFile)
            a = menu.exec_(menuPos)
            if not a: return

            actionText = str(a.text())
            if actionText.startswith('Recover '):
                self.__revertFile(itemName)
            else:
                l = len(targetFile) + 22
                renameTarget = actionText[l:]
                self.vcs.fileMoveDetected(targetFile, renameTarget)
            self.__rescanFiles()
            self.__refreshFileList(False)

        # Context menu for 'A' 'M' and 'R' (and 'a', 'm', 'r')
        if targetType in self.autoSelectTypes:
            menu = QtGui.QMenu()
            if targetFile in self.changeSelectedFiles:
                menu.addAction("Reset selection of changes")
            elif targetType == 'M' and self.twowayTool:
                menu.addAction("Select changes to commit")
            if targetType not in ['a', 'm', 'r']:
                menu.addAction("Revert %s to last revisioned state" % targetFile)
            if targetType not in ['R', 'r'] and self.editTool:
                menu.addAction("Open in %s" % os.path.basename(self.editTool))
            if targetType in ['M', 'A'] and self.diffTool:
                menu.addAction("Visual diff")
                if self.patchRefreshMode:
                    menu.addAction("Visual diff of all patch changes")
            elif targetType in ['m', 'a'] and self.diffTool:
                menu.addAction("Visual diff of all patch changes")
            a = menu.exec_(menuPos)
            if not a: return

            actionText = str(a.text())
            if actionText.startswith('Open '):
                runProgram([self.editTool, targetFile], expectedexits=[0,1,255])
                self.vcs.dirtyCache(targetFile)
            elif actionText.startswith('Revert '):
                self.__revertFile(itemName)
                self.__rescanFiles()
            elif actionText.startswith('Visual diff'):
                if actionText.endswith('all patch changes'):
                    args = ['--rev', '-2', targetFile ]
                else:
                    args = [ targetFile ]
                runProgram(self.diffTool.split(' ') + args, expectedexits=[0,1,255])
                self.vcs.dirtyCache(targetFile)
            elif actionText.startswith('Select '):
                self.__selectChanges(targetFile)
            elif actionText.startswith('Reset '):
                self.__resetChangeSelection(targetFile)
            self.__refreshFileList(False)

    def __selectChanges(self, workingFile):
        '''User would like to select changes made to this file for commit,
           unselected changes are left in working directory after commit or
           at exit.
        '''
        self.vcs.dirtyCache(workingFile)
        workingCopy = '.qct/' + workingFile + '.orig'
        try:
            path = os.path.dirname(workingFile)
            os.makedirs('.qct/' + path)
        except OSError:
            pass
        try:
            os.remove(workingCopy)
        except OSError:
            pass
        try:
            os.rename(workingFile, workingCopy)
        except:
            return
        self.changeSelectedFiles.append(workingFile)
        try:
            self.vcs.generateParentFile(workingFile)
            runProgram([self.twowayTool, workingCopy, workingFile])
        except:
            print "Change selection failed, returning working file"
            self.__resetChangeSelection(workingFile)

    def __resetChangeSelection(self, workingFile):
        '''Restore original working copy, clean up .qct/'''
        i = self.changeSelectedFiles.index(workingFile)
        del self.changeSelectedFiles[i]
        self.vcs.dirtyCache(workingFile)
        workingCopy = '.qct/' + workingFile + '.orig'
        try:
            os.remove(workingFile)
        except OSError:
            pass
        os.rename(workingCopy, workingFile)
        try:
            path = os.path.dirname(workingFile)
            if path: os.removedirs('.qct/' + path)
            os.removedirs('.qct/')
        except OSError:
            pass

    def __updateCommitButtonState(self):
        '''Only enable the commit button if a valid log message exists
           and one or more files are selected
        '''
        logMessage = self.ui.commitTextEntry.toPlainText()
        if (logMessage != self.logTemplate or self.patchRefreshMode) and self.getCheckedFiles():
            self.ui.commitPushButton.setEnabled(True)
            self.ui.commitPushButton.setToolTip(QtGui.QApplication.translate("commitToolDialog",
                self.commitButtonToolTip, None, QtGui.QApplication.UnicodeUTF8))
        else:
            self.ui.commitPushButton.setEnabled(False)
            self.ui.commitPushButton.setToolTip(QtGui.QApplication.translate("commitToolDialog",
                'Disabled until file(s) are selected and a log message is entered',
                None, QtGui.QApplication.UnicodeUTF8))

    def __revertFile(self, fileName):
        if QtGui.QMessageBox.warning(self, "Revert Warning",
                "Are you sure you want to revert %s?" % fileName[2:],
                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) != QtGui.QMessageBox.Ok:
            return
        self.vcs.revertFiles([ fileName ])

    def __detectFileCopySource(self, targetFile):
        '''The user has identified an unknown file as a copy of a revisioned
           file.  Allow the user to select the copy source by opening a file
           selection dialog
        '''
        ext = os.path.splitext(targetFile)[1]
        if ext:
            searchExtensions = '%s Files (*%s);;All Files (*)' % (ext[1:].capitalize(), ext)
        else:
            searchExtensions = 'All Files (*)'

        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                         "Select copy source of %s" % targetFile,
                                         targetFile, searchExtensions)
        if not fileName.isEmpty():
            self.vcs.fileCopyDetected(str(fileName), targetFile)


    def __saveLogMessage(self, logMessage):
        '''A new commit (or abort) has occurred, try to save the log message.
           If the message is a duplicate of a message already in the history,
           then move it to the top of the stack
        '''
        if logMessage and logMessage != self.logTemplate:
            if logMessage in self.logHistory:
                self.logHistory.remove(logMessage)
            self.logHistory.append(logMessage)
            if len(self.logHistory) > self.maxHistCount:
                del self.logHistory[0]

    def __fillLogHistCombo(self):
        '''Fill the log history drop-down box with the last N messages'''
        for log in self.logHistory:
            topLine = log.split('\n')[0]
            self.ui.logHistComboBox.insertItem(0, topLine)
        self.ui.logHistComboBox.setCurrentIndex(0)

    def on_prefPushButton_pressed(self):
        '''Preferences Dialog'''
        prefDialog = PrefDialog()
        prefDialog.show()
        prefDialog.exec_()

        oldIgnored = self.showIgnored
        self.__retrieveConfigurables()
        if self.showIgnored != oldIgnored:
            self.__rescanFiles()
            self.__refreshFileList(False)
            self.__updateCommitButtonState()

    @QtCore.pyqtSignature("int")
    def on_logHistComboBox_activated(self, row):
        '''The user has selected a log entry from the history drop-down'''
        index = len(self.logHistory) - row - 1
        self.ui.commitTextEntry.clear()
        self.ui.commitTextEntry.setFocus()
        self.ui.commitTextEntry.setPlainText(self.logHistory[index])

    def closeEvent(self, e = None):
        '''Dialog is closing, save persistent state'''

        # Recover working directory first, priorities...
        for targetFile in self.changeSelectedFiles:
            self.__resetChangeSelection(targetFile)
        self.changeSelectedFiles = []

        # Save off any aborted log message
        logMessage = self.ui.commitTextEntry.toPlainText()
        self.__saveLogMessage(logMessage)

        settings = QtCore.QSettings('vcs', 'qct')
        settings.beginGroup('mainwindow')
        settings.setValue("size", QtCore.QVariant(self.size()))
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("splitter", QtCore.QVariant(self.ui.splitter.saveState()))
        settings.endGroup()
        settings.beginGroup('commitLog')
        settings.beginWriteArray('history')
        for i in xrange(len(self.logHistory)):
            settings.setArrayIndex(i)
            log = self.logHistory[i]
            settings.setValue("text", QtCore.QVariant(log))
        settings.endArray()
        settings.endGroup()

        settings.sync()
        if e is not None:
            e.accept()

    def __pageDownBrowser(self):
        '''Page Up the diff browser (Ctrl-])'''
        vs = self.ui.diffBrowser.verticalScrollBar()
        vs.triggerAction(QtGui.QAbstractSlider.SliderPageStepAdd)

    def __pageUpBrowser(self):
        '''Page Up the diff browser (Ctrl-[)'''
        vs = self.ui.diffBrowser.verticalScrollBar()
        vs.triggerAction(QtGui.QAbstractSlider.SliderPageStepSub)

    def __displaySelectedFile(self):
        '''Show status of currently selected file'''
        item = self.itemList[ self.displayedRow ]
        deltaText = self.vcs.getFileStatus(item)
        #self.ui.diffBrowser.setPlainText(deltaText)
        self.ui.diffBrowser.setHtml(formatPatchRichText(deltaText, self.patchColors))
        self.ui.diffBrowserBox.setTitle(item[2:] + " file status")

    def __refreshFileList(self, newCommitFlag):
        '''Refresh the file list, display status of first file'''
        if not self.itemList:
            print "No remaining uncommited changes"
            self.close()
            return

        if newCommitFlag:
            self.fileCheckState = {}

        self.ui.fileListWidget.clear()
        self.unknownFileList = []
        for itemName in self.itemList:
            listItem = QtGui.QListWidgetItem(itemName)
            status = itemName[0]
            fileName = itemName[2:]
            if status == '?':
                self.unknownFileList.append(fileName)
            if newCommitFlag and status in self.autoSelectTypes:
                listItem.setCheckState(QtCore.Qt.Checked)
                self.fileCheckState[ fileName ] = True
            elif self.fileCheckState.has_key(fileName) and self.fileCheckState[ fileName ] == True:
                listItem.setCheckState(QtCore.Qt.Checked)
            else:
                listItem.setCheckState(QtCore.Qt.Unchecked)
                self.fileCheckState[ fileName ] = False
            self.ui.fileListWidget.addItem(listItem)

        # Display status (diff) of first item in list, and select it
        self.displayedRow = 0
        self.__displaySelectedFile()
        item = self.ui.fileListWidget.item(0)
        self.ui.fileListWidget.setItemSelected(item, True)
        self.ui.fileListWidget.setCurrentItem(item)

        # Refresh log template if necessary
        if newCommitFlag or self.patchRefreshMode:
            self.logTemplate = self.vcs.getLogTemplate()

        # Prepare for new commit message
        if newCommitFlag:
            self.ui.commitTextEntry.clear()
            self.ui.commitTextEntry.setFocus()
            self.ui.commitTextEntry.setPlainText(self.logTemplate)
        self.__updateCommitButtonState()

    def on_commitTextEntry_textChanged(self):
        '''User has typed something in the commit text window'''
        self.__updateCommitButtonState()

    def unselectAll(self):
        '''Reset checked state of all files (Ctrl-U)'''
        self.fileCheckState = {}
        self.__refreshFileList(False)

    def getCheckedFiles(self):
        '''Helper function to build list of checked (selected) files'''
        checkedItemList = []
        for item in self.itemList:
            fileName = item[2:]
            if self.fileCheckState[ fileName ] == True:
                checkedItemList.append(item)
        return checkedItemList

    def displayNextFile(self):
        '''User has hit CTRL-N'''
        item = self.ui.fileListWidget.item(self.displayedRow)
        self.ui.fileListWidget.setItemSelected(item, False)

        self.displayedRow += 1
        if self.displayedRow >= len(self.itemList):
            self.displayedRow = 0

        item = self.ui.fileListWidget.item(self.displayedRow)
        self.ui.fileListWidget.setCurrentItem(item)
        self.ui.fileListWidget.setItemSelected(item, True)
        self.ui.fileListWidget.scrollToItem(item)
        self.__displaySelectedFile()

    def commitSelected(self):
        '''Commit selected files, then refresh the dialog for next commit'''
        checkedItemList = self.getCheckedFiles()
        if not checkedItemList:
            QtGui.QMessageBox.warning(self, "Commit Warning",
                "No files are selected, nothing to commit", QtGui.QMessageBox.Ok)
            self.ui.fileListWidget.setFocus()
            return

        logMessage = self.ui.commitTextEntry.toPlainText()
        if not logMessage or logMessage == self.logTemplate:
            QtGui.QMessageBox.warning(self, "Commit Warning",
                "No log message specified, aborting commit", QtGui.QMessageBox.Ok)
            self.ui.commitTextEntry.setFocus()
            return

        self.vcs.commitFiles(checkedItemList, str(logMessage))
        self.__saveLogMessage(logMessage)
        self.__fillLogHistCombo()

        # Put back unselected changes (original working copies) and
        # clean up .qct/ directory
        for targetFile in self.changeSelectedFiles:
            self.__resetChangeSelection(targetFile)
        self.changeSelectedFiles = []

        self.__rescanFiles()
        self.__refreshFileList(True)

    def on_selectAllPushButton_pressed(self):
        '''(Un)Select All button has been pressed'''
        # Try to select all items
        changedFileState = False
        for item in self.itemList:
            f = item[2:]
            if self.fileCheckState[ f ] == False:
                self.fileCheckState[ f ] = True
                changedFileState = True
        # If there were no un-selected items, toggle unselect them all
        if changedFileState == False:
            self.fileCheckState = { }
        self.__refreshFileList(False)

    def on_refreshPushButton_pressed(self):
        '''Refresh button pressed slot handler'''
        oldSelectState = self.fileCheckState
        self.fileCheckState = {}
        self.__rescanFiles()
        for item in self.itemList:
            f = item[2:]
            if oldSelectState.has_key(f) and oldSelectState[ f ] == True:
                self.fileCheckState[ f ] = True
            else:
                self.fileCheckState[ f ] = False
        self.__refreshFileList(False)
        self.__updateCommitButtonState()

    def on_fileListWidget_itemActivated(self, item):
        '''The user has activated a list item, we toggle its check state'''
        # These will trigger cell change signals
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def on_fileListWidget_itemChanged(self, item):
        '''The user has modified the check state of an item,
           If the item was part of a select group we set them all to the
           checked state of the modified item.'''
        if self.itemChangeEntered: return
        self.itemChangeEntered = True

        if item.checkState() == QtCore.Qt.Checked:
            selectedItemList = self.ui.fileListWidget.selectedItems()
            if item in selectedItemList:
                for si in selectedItemList: 
                    fileName = str(si.text())[2:]
                    si.setCheckState(QtCore.Qt.Checked)
                    self.fileCheckState[ fileName ] = True
            else:
                fileName = str(item.text())[2:]
                item.setCheckState(QtCore.Qt.Checked)
                self.fileCheckState[ fileName ] = True
        else:
            selectedItemList = self.ui.fileListWidget.selectedItems()
            if item in selectedItemList:
                for si in selectedItemList: 
                    fileName = str(si.text())[2:]
                    si.setCheckState(QtCore.Qt.Unchecked)
                    self.fileCheckState[ fileName ] = False
            else:
                fileName = str(item.text())[2:]
                item.setCheckState(QtCore.Qt.Unchecked)
                self.fileCheckState[ fileName ] = False

        self.__updateCommitButtonState()
        self.itemChangeEntered = False

    def on_fileListWidget_itemClicked(self, item):
        '''The user has clicked on a list item'''
        row = self.ui.fileListWidget.row(item)
        if row != -1 and self.itemList and row != self.displayedRow:
            self.displayedRow = row
            self.__displaySelectedFile()
        self.__updateCommitButtonState()

    def on_fileListWidget_itemSelectionChanged(self):
        '''The user has selected a list item'''
        row = self.ui.fileListWidget.currentRow()
        if row != -1 and self.itemList and row != self.displayedRow:
            if row >= len(self.itemList):
                row = 0
            self.displayedRow = row
            self.__displaySelectedFile()

class PrefDialog(QtGui.QDialog):
    '''QCT Preferences Dialog'''
    def __init__(self):
        QtGui.QDialog.__init__(self)

        self.ui = Ui_prefDialog()
        self.ui.setupUi(self)

        settings = QtCore.QSettings('vcs', 'qct')
        settings.beginGroup('fileList')
        self.showIgnored = settings.value('showIgnored', QtCore.QVariant(False)).toBool()
        self.wrapList = settings.value('wrapping', QtCore.QVariant(False)).toBool()
        settings.endGroup()
        
        settings.beginGroup('tools')
        self.diffTool = settings.value('diffTool', QtCore.QVariant('')).toString()
        self.editTool = settings.value('editTool', QtCore.QVariant('')).toString()
        self.twowayTool = settings.value('twowayTool', QtCore.QVariant('')).toString()
        settings.endGroup()

        # Disable wrap feature for Qt < 4.2
        try:
            from PyQt4 import pyqtconfig
        except ImportError:
            # The Windows installed PyQt4 does not support pyqtconfig, but
            # does support wrapping, etc.  So we will leave this feature
            # enabled if we fail to import pyqtconfig.
            # self.ui.wrapListCheckBox.setEnabled(False)
            pass
        else:
            pyqtconfig = pyqtconfig.Configuration()
            if pyqtconfig.qt_version < 0x40200:
                self.wrapList = False
                self.ui.wrapListCheckBox.setEnabled(False)
                self.ui.wrapListCheckBox.setToolTip(QtGui.QApplication.translate("wrapListCheckBox",
                    "This feature requires Qt >= 4.2", None, QtGui.QApplication.UnicodeUTF8))

        self.ui.ignoredButton.setChecked(self.showIgnored)
        self.ui.wrapListCheckBox.setChecked(self.wrapList)
        self.ui.diffToolEdit.setText(self.diffTool)
        self.ui.mergeToolEdit.setText(self.twowayTool)
        self.ui.editToolEdit.setText(self.editTool)

    def on_diffToolBrowseButton_pressed(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select a diff tool", '', 'All Files (*)')
        if not fileName.isEmpty():
            self.ui.diffToolEdit.setText(fileName)

    def on_mergeToolBrowseButton_pressed(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select a two-way merge tool", '', 'All Files (*)')
        if not fileName.isEmpty():
            self.ui.mergeToolEdit.setText(fileName)

    def on_editToolBrowseButton_pressed(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Select an external editor", '', 'All Files (*)')
        if not fileName.isEmpty():
            self.ui.editToolEdit.setText(fileName)

    def on_wrapListCheckBox_toggled(self):
        '''Wrap List button toggled slot handler'''
        self.wrapList = self.ui.wrapListCheckBox.isChecked()

    def on_ignoredButton_toggled(self):
        '''Ignore button toggled slot handler'''
        self.showIgnored = self.ui.ignoredButton.isChecked()

    def accept(self):
        settings = QtCore.QSettings('vcs', 'qct')
        settings.beginGroup('fileList')
        settings.setValue('showIgnored', QtCore.QVariant(self.ui.ignoredButton.isChecked()))
        settings.setValue('wrapping', QtCore.QVariant(self.ui.wrapListCheckBox.isChecked()))
        settings.endGroup()
        self.diffTool = str(self.ui.diffToolEdit.text())
        self.twowayTool = str(self.ui.mergeToolEdit.text())
        self.editTool = str(self.ui.editToolEdit.text())
        settings.beginGroup('tools')
        settings.setValue('diffTool', QtCore.QVariant(self.diffTool))
        settings.setValue('editTool', QtCore.QVariant(self.editTool))
        settings.setValue('twowayTool', QtCore.QVariant(self.twowayTool))
        settings.endGroup()
        settings.sync()
        self.close()
