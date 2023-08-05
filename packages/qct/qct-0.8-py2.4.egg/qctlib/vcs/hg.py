# Mercurial VCS back-end code for qct
#
# Copyright 2006 Steve Borho
#
# This software may be used and distributed according to the terms
# of the GNU General Public License, incorporated herein by reference.

import os
from stat import *
from qctlib.utils import runProgram, findInSystemPath, scanDiffOutput, isBinary

class qctVcsHg:
    def initRepo(self, argv):
        '''Initialize your revision control system, open repository'''

        # Find the mercurial binary name
        if findInSystemPath('hg') != None:
            self.hg_exe = 'hg'
        elif findInSystemPath('hg.cmd') != None:
            self.hg_exe = 'hg.cmd'
        elif findInSystemPath('hg.bat') != None:
            self.hg_exe = 'hg.bat'
        elif findInSystemPath('hg.exe') != None:
            self.hg_exe = 'hg.exe'
        else:
            print "Unable to find hg (.exe, .bat, .cmd) in your path"
            return -1

        # Verify we have a valid repository
        output = runProgram([self.hg_exe, 'root'], expectedexits=[0,255])
        self.repoRoot = output[:-len(os.linesep)]
        if output.startswith("abort"):
            print output
            return -1

        if os.getcwd() == self.repoRoot:
            self.runningFromRoot = True
        else:
            self.runningFromRoot = False

        self.stateNames = { 'M' : 'modified',
                'R' : 'removed',
                '!' : 'missing',
                '?' : 'unknown' }

        self.capList = [
                'ignore',      # VCS supports ignore masks (addIgnoreMask)
                'copy',        # VCS supports revisioned copying of files (fileMoveDetected)
                'rename',      # VCS supports revisioned renames (fileMoveDetected)
                'symlink',     # VCS supports symlinks
                'patchqueue',  # VCS supports patch queue (isPatchQueue, topPatchName)
                'progressbar'] # back-end supports a progress bar

        self.cmdLineOptions = []

        # To enable an auto-matic sign-off message:
        # [qct]
        # signoff = Sign-Off: Steve Borho
        self.signOff = runProgram([self.hg_exe, 'debugconfig', 'qct.signoff'])

        # Determine if this repository has any applied Mercurial Queue patches
        output = runProgram([self.hg_exe, 'qheader'], expectedexits=[0,1,255])
        recs = output.split(os.linesep)
        if recs[0] == 'No patches applied':
            self.isPatchQ = False
            return 0
        if recs[0] == "hg: unknown command 'qheader'":
            self.isPatchQ = False
            return 0
        else:
            # Patches only make sense from repository root
            if not self.runningFromRoot:
                print "Changing context to repository root: " + self.repoRoot
                os.chdir(self.repoRoot)
                self.runningFromRoot = True
            self.isPatchQ = True
            return 0

    def pluginOptions(self, opts):
        '''The Mercurial extension is passing along -I/-X command line options'''
        for epath in opts['exclude']:
            self.cmdLineOptions += ['-X', epath]
        for ipath in opts['include']:
            self.cmdLineOptions += ['-I', ipath]

    def capabilities(self):
        '''Return a list of optional capabilities supported by this VCS'''
        return self.capList

    def generateParentFile(self, workingFile):
        '''The GUI needs this file's parent revision in place so the user
           can select individual changes for commit (basically a revert)
        '''
        runProgram([self.hg_exe, 'cat', '--output', '%d/%s', workingFile])

    def addIgnoreMask(self, newIgnoreMask):
        '''The user has provided a new ignoreMask to be added to revision control'''
        globString = 'syntax: glob'
        # Read existing .hgignore (possibly empty)
        try:
            f = open(os.path.join(self.repoRoot, '.hgignore'), 'rb')
            text = f.read()
            f.close()
            iLines = text.split(os.linesep)
        except IOError:
            iLines = []
        # Find 'syntax: glob' line, add at end if not found
        if globString in iLines:
            line = iLines.index(globString)
        else:
            iLines.append(globString)
            line = len(iLines)
        # Insert new mask after 'syntax: glob' line
        iLines.insert(line + 1, newIgnoreMask)
        try:
            f = open(os.path.join(self.repoRoot, '.hgignore'), 'w')
            f.write(os.linesep.join(iLines))
            f.close()
            print "Added '%s' to ignore mask" % newIgnoreMask
        except IOError, e:
            print "Unable to add '%s' to ignore mask" % newIgnoreMask
            print e

    def fileMoveDetected(self, origFileName, newFileName):
        '''User has associated an unknown file with a missing file, describing
           a move/rename which occurred outside of revision control'''
        runProgram([self.hg_exe, 'mv', '--after', origFileName, newFileName])
        print "Recording move of %s to %s" % (origFileName, newFileName)

    def fileCopyDetected(self, origFileName, newFileName):
        '''User has associated an unknown file with an existing file, describing
           a copy which occurred outside of revision control'''
        runProgram([self.hg_exe, 'cp', '--after', origFileName, newFileName])
        print "Recording copy of %s to %s" % (origFileName, newFileName)

    def getLogTemplate(self):
        '''Request default log message template from VCS'''
        # If this repository has a patch queue with applied patches, then the
        # user is not commiting a changeset. they are refreshing the top patch.
        # So we put the current patch's description in the edit window.
        if self.isPatchQ:
            return runProgram([self.hg_exe, 'qheader'], expectedexits=[0,1,255])

        try:
            f = open(os.path.join(self.repoRoot, '.commit.template'), 'r')
            text = f.read()
            f.close()
        except IOError:
            text = ''
        return text

    def getAutoSelectTypes(self):
        '''Return annotations of file types which should be automatically
           selected when a new commit is started'''
        if self.isPatchQ:
            return ['A', 'M', 'R', 'a', 'm', 'r']
        else:
            return ['A', 'M', 'R']

    def isPatchQueue(self):
        '''Return true if Mercurial Queue patches are applied'''
        return self.isPatchQ

    def topPatchName(self):
        '''Return name of top patch (being refreshed)'''
        output = runProgram([self.hg_exe, 'qtop'])
        return output[:-1]

    def dirtyCache(self, fileName):
        '''The GUI would like us to forget cached data for this file'''
        if self.wdDiffCache.has_key(fileName):
            del self.wdDiffCache[fileName]

    def scanFiles(self, showIgnored, pb = None):
        '''Request scan for all commitable files from VCS, with optional
           progress bar
        '''
        # Called at startup, when 'Refresh' button is pressed, or when showIgnored toggled.
        self.patchDiffCache = {}
        self.wdDiffCache = {}

        # Cache changes in the working directory (parse and store hg diff).  The paths reported
        # by diff are always relative to the repo root, so if we're running outside of the root
        # directory there is no point in trying to pre-cache diffs.
        if self.runningFromRoot:
            diff = runProgram([self.hg_exe, 'diff', '--show-function'] + self.cmdLineOptions)
            (addedList, removedList, modifiedList, self.wdDiffCache) = scanDiffOutput(diff)

        if pb: pb.setValue(1)

        # Provides ARM, same as diff, plus unknown ? and missing !
        statusOutput = runProgram([self.hg_exe, 'status'] + self.cmdLineOptions + ['.'])
        recs = statusOutput.split(os.linesep)
        recs.pop() # remove last entry (which is '')

        if pb: pb.setValue(2)

        if showIgnored:
            statusOutput = runProgram([self.hg_exe, 'status', '-i'] + self.cmdLineOptions + ['.'])
            recs += statusOutput.split(os.linesep)
            recs.pop() # remove last entry (which is '')

        if pb: pb.setValue(3)

        annotatedFileList = [ ]
        workingDirList = [ ]
        for fileName in recs:
            if fileName.startswith('*** '): continue   # Skip error messages from hg status
            workingDirList.append(fileName[2:])
            annotatedFileList.append(fileName)

        if pb: pb.setValue(4)

        if self.isPatchQ:
            # Capture changes in the current patch (parse and store hg tip)
            qtop = runProgram([self.hg_exe, 'tip', '--patch'])
            (addedPList, removedPList, modifiedPList, self.patchDiffCache) = scanDiffOutput(qtop)

            # Add patch files which did not show up in `hg status`
            for f in addedPList:
                if f not in workingDirList: annotatedFileList.append('a ' + f)
            for f in removedPList:
                if f not in workingDirList: annotatedFileList.append('r ' + f)
            for f in modifiedPList:
                if f not in workingDirList: annotatedFileList.append('m ' + f)

        return annotatedFileList


    def __getWorkingDirChanges(self, fileName, type):
        if self.wdDiffCache.has_key(fileName):
            return self.wdDiffCache[fileName]

        # For symlinks, we return the link data
        if type not in ['R', '!']:
            lmode = os.lstat(fileName)[ST_MODE]
            if S_ISLNK(lmode):
                text = "Symlink: %s -> %s" % (fileName, os.readlink(fileName))
                self.wdDiffCache[fileName] = text
                return text

        # For revisioned files, we use hg diff
        if type in ['A', 'M', 'R']:
            text = runProgram([self.hg_exe, 'diff', '--show-function', fileName])
            self.wdDiffCache[fileName] = text
            return text

        # For unrevisioned files, we return file contents
        if type in ['?', 'I']:
            if isBinary(fileName):
                text = " <Binary File>"
            else:
                f = open(fileName)
                text = f.read()
                f.close()
            self.wdDiffCache[fileName] = text
            return text

        # For missing files, we use hg cat
        if type == '!':
            text = runProgram([self.hg_exe, 'cat', fileName])
            if not text: text = " <empty file>"
            elif '\0' in text: text = " <Binary File of %d KBytes>" % (len(text) / 1024)
            self.wdDiffCache[fileName] = text
            return text
        else:
            return "Unknown file type " + type


    def getFileStatus(self, itemName):
        '''Request file deltas from VCS'''
        if self.isPatchQ:
            return self._getPatchFileStatus(itemName)

        type = itemName[0]
        fileName = itemName[2:]
        text = self.__getWorkingDirChanges(fileName, type)

        # Useful shorthand vars.  Leading lines beginning with % are treated as RTF
        bFileName = "%<b>" + fileName + "</b>"
        noteLineSep = os.linesep + '%'

        if type == 'A':
            note = bFileName + " has been added to revision control or is a rename target, but has never been commited."
            return note + os.linesep + text
        elif type == 'M':
            note = bFileName + " has been modified in your working directory."
            return note + os.linesep + text
        elif type == '?':
            note = bFileName + " is not currently tracked. If commited, it will be added to revision control."
            return note + os.linesep + "= Unrevisioned File Contents" + os.linesep + text
        elif type == 'I':
            note = bFileName + " is usually ignored, but will be added to revision control if commited"
            return note + os.linesep + text
        elif type == 'R':
            note = bFileName + " has been marked for deletion, or renamed, but has not yet been commited"
            note += noteLineSep + "The file can be recovered by reverting it to it's last revisioned state."
            return note + os.linesep + "= Removed File Diffs" + os.linesep + text
        elif type == '!':
            note = bFileName + " was tracked but is now missing. If commited, it will be marked as removed in revision control."
            note += noteLineSep + "The file can be recovered by reverting it to it's last revisioned state."
            return note + os.linesep + "= Contents of Missing File" + os.linesep + text
        else:
            return "Unknown file type " + type


    def _getPatchFileStatus(self, itemName):
        '''Get status of a file, which may have patch diffs, and may have working directory diffs'''

        type = itemName[0]
        fileName = itemName[2:]

        # Useful shorthand vars.  Leading lines beginning with % are treated as RTF
        bFileName = "%<b>" + fileName + "</b>"
        noteLineSep = os.linesep + '%'

        if type == 'A':
            note = bFileName + " has been added to the working directory, but has not been included in this patch."
            note += noteLineSep + "If reverted, this file will return to an unrevisioned state."
            wtext = self.__getWorkingDirChanges(fileName, type)
            return note + os.linesep + "= Added File Diffs" + os.linesep + wtext
        elif type == 'a':
            note = bFileName + " is a new file provided by this patch.  "
            note += noteLineSep + "Reverting this file has no effect, it must be removed from the patch first."
            ptext = self.patchDiffCache[fileName]
            return note + os.linesep + "= Added File Diffs" + os.linesep + ptext
        elif type == '?':
            note = bFileName + " is not currently tracked. If commited, it will appear to be provided by this patch.  "
            note += noteLineSep + "Reverting this file has no effect."
            wtext = self.__getWorkingDirChanges(fileName, type)
            return note + os.linesep + "= Unrevisioned File Contents" + os.linesep + wtext
        elif type == 'I':
            note = bFileName + " is usually ignored, but will be recorded as provided by this patch if commited.  "
            note += noteLineSep + "Reverting this file has no effect."
            wtext = self.__getWorkingDirChanges(fileName, type)
            return note + os.linesep + "= Unrevisioned File Contents" + os.linesep + wtext
        elif type == '!':
            note = bFileName + " was tracked but is now missing, will be marked as removed by this patch if commited.  "
            note += noteLineSep + "If reverted, this file will be recovered to last revisioned state."
            wtext = self.__getWorkingDirChanges(fileName, type)
            return note + os.linesep + "= Contents of Missing File" + os.linesep + wtext
        elif type == 'R':
            note = bFileName + " has been marked for deletion in your working directory, but has not yet been commited.  "
            note += noteLineSep + "If reverted, this file will be recovered to it's last revisioned state."
            wtext = self.__getWorkingDirChanges(fileName, type)
            return note + os.linesep + "= Removed File Diffs" + os.linesep + wtext
        elif type == 'r':
            note = bFileName + " is deleted by this patch"
            note += noteLineSep + "If you remove this file from the patch, it will appear removed in your working dir, "
            note += noteLineSep + "at which point you can revert it to it's last revisioned state."
            ptext = self.patchDiffCache[fileName]
            return note + os.linesep + "= Removed File Diffs" + os.linesep + ptext
        elif type == 'M':
            wtext = self.__getWorkingDirChanges(fileName, type)
            if self.patchDiffCache.has_key(fileName):
                note = bFileName + " has changes recorded in the patch, and further changes in the working directory "
                note += noteLineSep + "If reverted, only the working directory changes will be removed.  "
                note += noteLineSep + "If you refresh without this file, all changes will be left in your working directory."
                ptext = self.patchDiffCache[fileName]
                status = note + os.linesep + "= Working Directory Diffs" + os.linesep + wtext
                status += os.linesep + "= Patch Diffs" + os.linesep + ptext
            else:
                note = bFileName + " has changes in the working directory that are not yet included in this patch."
                note += noteLineSep + "If reverted, the working directory diffs will be removed."
                status = note + os.linesep + "= Working Directory Diffs" + os.linesep + wtext
            return status
        elif type == 'm':
            note = bFileName + " is modified by this patch.  There are no further changes in the working directory so "
            note += noteLineSep + "reverting this file will have no effect.  If you remove this file from the patch "
            note += noteLineSep + "these modifications will be left in the working directory."
            ptext = self.patchDiffCache[fileName]
            return note + os.linesep + "= Patch Diffs" + os.linesep + ptext
        else:
            return "Unknown file type " + type


    def commitFiles(self, selectedFileList, logMsgText):
        '''Commit selected files'''
        # Files in list are annotated (A, M, etc) so this function can
        # mark files for add or delete as necessary before instigating the commit.
        commitFileNames = []
        addFileList = []
        removeFileList = []
        for f in selectedFileList:
            type = f[0]
            fileName = f[2:]
            commitFileNames.append(fileName)
            if type in ['?', 'I']: addFileList.append(fileName)
            elif type == '!': removeFileList.append(fileName)

        if addFileList:
            runProgram([self.hg_exe, 'add'] + addFileList)
            print "Added %d file(s) to revision control: %s" % (len(addFileList), ', '.join(addFileList))

        if removeFileList:
            runProgram([self.hg_exe, 'rm'] + removeFileList)
            print "Removed %d file(s) from revision control: %s" % (len(removeFileList), ', '.join(removeFileList))

        if self.signOff:
            logMsgText += os.linesep + self.signOff

        if self.isPatchQ:
            runProgram([self.hg_exe, 'qrefresh', '-l', '-'] + commitFileNames, logMsgText)
            print self.topPatchName() + " refreshed with %d file(s): %s" \
                    % (len(commitFileNames), ', '.join(commitFileNames))
        else:
            runProgram([self.hg_exe, 'commit', '-l', '-'] + commitFileNames, logMsgText)
            print "%d file(s) commited: %s" % (len(commitFileNames), ', '.join(commitFileNames))

    def revertFiles(self, selectedFileList):
        '''Revert selected files to last revisioned state'''
        revertFileNames = []
        for f in selectedFileList:
            type = f[0]
            fileName = f[2:]
            if type in ['R', '!', 'M']:
                prevState = self.stateNames[type]
                print "%s recovered to last revisioned state (was %s)" % (fileName, prevState)
                revertFileNames.append(fileName)
            elif type == 'A':
                print "%s removed from revision control (was added)" % fileName
                revertFileNames.append(fileName)
            else:
                print "File %s not reverted" % fileName

        if revertFileNames:
            runProgram([self.hg_exe, 'revert'] + revertFileNames)
        else:
            print "No revertable files"

# vim: tw=120
