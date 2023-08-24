#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from enum import Enum, auto

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import config
from language import translations
import ndstool
import xdelta3
import pokeversion

import edittext
import editpokemon
import editmoves
import editdlg

class version:
    major = 0
    minor = 2
    revision = 0


if "--help" in sys.argv or "-h" in sys.argv:
    print("""Project Pokemon ROM Editor 2 - 2023
Usage: %s [-l|-n] [-d]
Options:
 --load/-l <dir>            Loads a project folder
 --new /-n ndsfile.nds      Creates a new project from a ROM
 --dlg /-d dialog           Starts a dialog

Dialogs:
 text           Text Editor
 move           Move Editor
 pokemon        Pokemon Editor""" % (sys.argv[0]))
    exit()

restart = False

class StartAction(Enum):
    Empty = auto(),
    NewNDS = auto(),
    OpenFolder = auto(),

class StartAction2(Enum):
    Empty = auto(),
    Text = auto(),
    Move = auto(),
    Pokemon = auto(),

class MainWindow(QMainWindow):
    def __init__(self, app: QApplication, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.app = app

        self.preProcess()
        self.setupUi()
        self.postProcess()

    def preProcess(self):
        self._projFolder = None
        self.openedHisRecorder = config.OpenedHistoyRecorder()
        config.mw = self
        self.dirty = False

        self.start_args = {}
        self.start_action = StartAction.Empty
        self.start_action2 = StartAction2.Empty

        print(sys.argv)

        args = sys.argv[1:]

        if args:
            while args:
                arg = args.pop(0)
                if arg in ["-l", "--load"]:
                    self.start_args['projFolder'] = args.pop(0)
                    self.start_action = StartAction.OpenFolder
                    self.openedHisRecorder.push(self.start_args['projFolder'])

                elif arg in ["-n", "--new"]:
                    self.start_args['ndsFile'] = args.pop(0)
                    self.start_action = StartAction.NewNDS

                elif arg in ["-d", "--dialog"]:
                    arg = args.pop(0)

                    if arg == "text":
                        self.start_action2 = StartAction2.Text
                    elif arg == "pokemon":
                        self.start_action2 = StartAction2.Pokemon
                    elif arg == "move":
                        self.start_action2 = StartAction2.Move
                else:
                    print("Unrecognized argument: %s" % arg, file=sys.stderr)
        else:
            records = self.openedHisRecorder.fetch()

            if records:
                self.start_action = StartAction.OpenFolder
                self.start_args['projFolder'] = records[0]

    def postProcess(self):
        match self.start_action:
            case StartAction.OpenFolder:
                self.openProjectOf(self.start_args['projFolder'])

            case StartAction.NewNDS:
                self.newProjectOf(self.start_args['ndsFile'])

        match self.start_action2:
            case StartAction2.Text:
                edittext.create()

            case StartAction2.Pokemon:
                editpokemon.create()

            case StartAction2.Move:
                editmoves.create()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("PPRE-II v%i.%i.%i" %
                            (version.major, version.minor, version.revision))
        self.app.setApplicationName("PPRE")
        self.app.setApplicationVersion("%i.%i.%i" %
                                       (version.major, version.minor, version.revision))
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.app.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translations["menu_file"])
        self.menutasks = {}
        self.menutasks["newproject"] = QAction(self.menus["file"])
        self.menutasks["newproject"].setText(translations["menu_newproject"])
        self.menutasks["newproject"].setShortcut("CTRL+N")
        self.menus["file"].addAction(self.menutasks["newproject"])
        self.menutasks["newproject"].triggered.connect(self.newProject)

        self.menutasks["openproject"] = QAction(self.menus["file"])
        self.menutasks["openproject"].setText(translations["menu_openproject"])
        self.menutasks["openproject"].setShortcut("CTRL+O")
        self.menus["file"].addAction(self.menutasks["openproject"])
        self.menutasks["openproject"].triggered.connect(self.openProject)

        open_recently_menu = QMenu(self.menus["file"])
        open_recently_menu.setTitle(translations["menu_open_recently"])

        for rec in self.openedHisRecorder.fetch()[1:]:
            act = QAction(rec, parent=open_recently_menu)
            open_recently_menu.addAction(act)

        open_recently_menu.triggered.connect(lambda action: self.restartOpenProject(action.text()))

        self.menutasks['open_recently'] = open_recently_menu
        self.menus["file"].addMenu(self.menutasks["open_recently"])

        self.menutasks["exportrom"] = QAction(self.menus["file"])
        self.menutasks["exportrom"].setText(translations["menu_exportrom"])
        self.menus["file"].addAction(self.menutasks["exportrom"])
        self.menutasks["exportrom"].triggered.connect(self.exportRom)

        self.menutasks["makepatch"] = QAction(self.menus["file"])
        self.menutasks["makepatch"].setText(translations["menu_makepatch"])
        self.menus["file"].addAction(self.menutasks["makepatch"])
        self.menutasks["makepatch"].triggered.connect(self.makePatch)

        self.menutasks["quit"] = QAction(self.menus["file"])
        self.menutasks["quit"].setText(translations["menu_quit"])
        self.menutasks["quit"].setShortcut("CTRL+Q")
        self.menus["file"].addAction(self.menutasks["quit"])
        self.menutasks["quit"].triggered.connect(lambda: self.close())

        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.widgetcontainer.setObjectName("widgetcontainer")
        self.menus["edit"] = QMenu(self.menubar)
        self.menus["edit"].setTitle(translations["menu_edit"])
        self.menutasks["edittext"] = QAction(self.menus["edit"])
        self.menutasks["edittext"].setText(translations["menu_edittext"])
        self.menus["edit"].addAction(self.menutasks["edittext"])
        self.menutasks["edittext"].triggered.connect(edittext.create)
        self.menutasks["editpokemon"] = QAction(self.menus["edit"])
        self.menutasks["editpokemon"].setText(translations["menu_editpokemon"])
        self.menus["edit"].addAction(self.menutasks["editpokemon"])
        self.menutasks["editpokemon"].triggered.connect(editpokemon.create)
        self.menutasks["editmoves"] = QAction(self.menus["edit"])
        self.menutasks["editmoves"].setText(translations["menu_editmoves"])
        self.menus["edit"].addAction(self.menutasks["editmoves"])
        self.menutasks["editmoves"].triggered.connect(editmoves.create)
        self.menubar.addAction(self.menus["edit"].menuAction())
        self.projectinfo = {}
        i = 0
        for sect in config.sections:
            for opt in config.options[sect]:
                self.projectinfo[sect+"_"+opt+"_name"] = QLabel(
                    self.widgetcontainer)
                self.projectinfo[sect+"_"+opt+"_name"].setGeometry(
                    QRect(30, 30*(i+1), 150, 25))
                self.projectinfo[sect+"_"+opt+"_name"].setText(
                    translations["config_%s_name" % (sect+"_"+opt)]+":")
                self.projectinfo[sect+"_"+opt+"_value"] = QLineEdit(
                    self.widgetcontainer)
                self.projectinfo[sect+"_"+opt+"_value"].setGeometry(
                    QRect(180, 30*(i+1), 150, 25))
                i += 1
        self.projectinfo['location_directory_value'].setReadOnly(True)
        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)
        self.resize(600, 400)
        editdlg.center_screen(self)

    @property
    def projFolder(self):
        return self._projFolder

    @projFolder.setter
    def projFolder(self, val):
        """ BE CAREFUL: It woulld determine proj file saving destination """

        self._projFolder = val
        self.projFile = os.path.join(self._projFolder, '.pprj')
        self.openedHisRecorder.push(self.projFolder)

    def openProject(self):
        projFolder = QFileDialog.getExistingDirectory(
            None,
            "Open PPRE Project Folder"
        )
        if projFolder:
            # ensure the path's sep is os spec instead of fixed '/'
            projFolder = os.path.abspath(projFolder)
            self.restartOpenProject(projFolder)

    def restartOpenProject(self, projFolder, action2: StartAction2 = StartAction2.Empty):
        # save opened history
        self.openedHisRecorder.save()

        global restart
        restart = True

        sys.argv = sys.argv[:1]
        sys.argv.append('-l')
        sys.argv.append(projFolder)

        match action2:
            case StartAction2.Text:
                sys.argv.extend(['-d', 'text'])

            case StartAction2.Pokemon:
                sys.argv.extend(['-d', 'pokemon'])

            case StartAction2.Move:
                sys.argv.extend(['-d', 'move'])

        self.close()

    def openProjectOf(self, projFolder):
        self.projFolder = projFolder

        if os.path.exists(self.projFile):
            config.load(open(self.projFile, "r"),
                        config.qtSetter, self.projectinfo)
        else:
            self.set_default_projectinfo()

        self.set_project_config()

    def newProject(self):
        ndsFile = QFileDialog.getOpenFileName(None, "Open NDS ROM",
                                              filter="NDS Files (*.nds);;All Files (*.*)")[0]
        if ndsFile:
            self.newProjectOf(ndsFile)

    def newProjectOf(self, ndsFile):
        d, tail = os.path.split(os.path.abspath(ndsFile))
        name = os.path.splitext(tail)[0]
        d = os.path.join(d, name)

        if os.path.exists(d):
            prompt = QMessageBox.question(None, "Overwrite directory?",
                                          "%s already exists. Would you like this " % d.rstrip("/") +
                                          "to be overwritten with the project directory?\n" +
                                          "All contents will be deleted. This cannot be undone.",
                                          QMessageBox.Yes, QMessageBox.No)
            if prompt == QMessageBox.Yes:
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.unlink(d)
            else:
                return

        os.makedirs(d)
        ndstool.dump(ndsFile, d)
        shutil.copy(ndsFile, os.path.join(d, config.defaults['origin_nds_fn']))
        self.restartOpenProject(d, self.start_action2)
        self.start_action2 = StartAction.Empty

    def set_default_projectinfo(self):
        """ After projFolder is set """

        folderName = os.path.basename(self.projFolder)

        self.projectinfo["location_directory_value"].setText(self.projFolder)
        self.projectinfo["project_name_value"].setText(folderName)
        self.projectinfo["project_output_value"].setText(
            os.path.join(self.projFolder, folderName+'.nds'))

    def set_project_config(self):
        config.project = {"directory": self.projFolder}
        config.project["versioninfo"] = pokeversion.get(self.projFolder)

    def saveProject(self):
        if self.projFolder:
            config.write(open(self.projFile, "w"),
                         config.qtGetter, self.projectinfo)
            self.dirty = False

    def exportRom(self):
        self.exportRomTo(self.projectinfo["project_output_value"].text())

    def exportRomAs(self):
        ndsFile = str(QFileDialog.getSaveFileName(None, "Open Save ROM",
                                                  filter="NDS Files (*.nds);;All Files (*.*)"))[0]
        if ndsFile:
            self.exportRomTo(ndsFile)

    def exportRomTo(self, output):
        if not config.project:
            QMessageBox.critical(None, translations["error_noromloaded_title"],
                                 translations["error_noromloaded"])
            return
        ndstool.build(output, config.project["directory"])
        QMessageBox.information(None,
                                translations["ok_output_rom"],
                                output)

    def makePatch(self):
        if not config.project:
            QMessageBox.critical(None, translations["error_noromloaded_title"],
                                 translations["error_noromloaded"])
        inrom = os.path.join(self.projFolder, config.defaults['origin_nds_fn'])
        outrom = str(self.projectinfo["project_output_value"].text())
        if not os.path.exists(inrom):
            QMessageBox.critical(None, translations["error_noromloaded_title"],
                                 translations["error_nooriginalrom"])
            return
        if not os.path.exists(outrom):
            QMessageBox.critical(None, translations["error_noromloaded_title"],
                                 translations["error_nonewrom"])
            return
        patchFile = QFileDialog.getSaveFileName(None, "Save Patch File",
                                                filter="xdelta3 Patch Files (*.xdelta3);;All Files (*.*)")[0]
        if not patchFile:
            return
        xdelta3.makePatch(patchFile, inrom, outrom)

    def closeEvent(self, a0: QCloseEvent) -> None:
        self.saveProject()
        self.openedHisRecorder.save()
        super().closeEvent(a0)


if __name__ == '__main__':
    import signal

    # For convenience
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)

    while True:
        mw = MainWindow(app)

        if not restart:
            mw.show()
            app.exec()

        if not restart:
            break
        else:
            restart = False
