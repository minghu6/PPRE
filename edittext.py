#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from editdlg import EditDlg, center_screen
import config
from language import translations
import pokeversion
from nds import narc, txt

files = pokeversion.textfiles

class EditText(EditDlg):
    wintitle = "%s - Text Editor - PPRE"

    def __init__(self, parent=None):
        super(EditText, self).__init__(parent)

        self.setupUi()
        self.dirty = False
        self.openTextNarc("Main")
        # Why it doesn't works in `setupUi` ?
        center_screen(self)

    def setupUi(self):
        self.setObjectName("EditText")
        self.setWindowTitle(EditText.wintitle % "No file opened")
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translations["menu_file"])
        self.menubar.addAction(self.menus["file"].menuAction())
        self.menutasks = {}
        self.menutasks["newtext"] = QAction(self.menus["file"])
        self.menutasks["newtext"].setText(translations["menu_newtext"])
        self.menus["file"].addAction(self.menutasks["newtext"])
        self.menutasks["newtext"].triggered.connect(self.newText)
        for f in files[config.project["versioninfo"][0]]:
            self.menutasks["opentext_"+f] = QAction(self.menus["file"])
            self.menutasks["opentext_"+f].setText(
                translations["menu_opentext"]+": "+f)
            self.menus["file"].addAction(self.menutasks["opentext_"+f])
            func = lambda x: (lambda: self.openTextNarc(x))
            self.menutasks["opentext_"+f].triggered.connect(func(f))
        self.menutasks["savetext"] = QAction(self.menus["file"])
        self.menutasks["savetext"].setText(translations["menu_savetext"])
        self.menus["file"].addAction(self.menutasks["savetext"])
        self.menutasks["savetext"].triggered.connect(self.saveText)
        self.menutasks["close"] = QAction(self.menus["file"])
        self.menutasks["close"].setText(translations["menu_close"])
        self.menus["file"].addAction(self.menutasks["close"])
        self.menutasks["close"].triggered.connect(self.close)
        self.menubar.addAction(self.menus["file"].menuAction())
        self.menus["tools"] = QMenu(self.menubar)
        self.menus["tools"].setTitle(translations["menu_tools"])
        self.menutasks["search"] = QAction(self.menus["tools"])
        self.menutasks["search"].setText(translations["menu_search"])
        self.menus["tools"].addAction(self.menutasks["search"])
        self.menutasks["search"].triggered.connect(self.search)
        self.menubar.addAction(self.menus["tools"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.widgetcontainer.setObjectName("widgetcontainer")
        self.textfilelist = QComboBox(self.widgetcontainer)
        self.textfilelist.setGeometry(QRect(50, 25, 200, 20))
        self.prevfile = -1
        self.textfilelist.currentIndexChanged[int].connect(self.openText)

        self.textedit = QTextEdit(self.widgetcontainer)
        self.textedit.setGeometry(QRect(50, 50, 500, 300))
        self.textedit.setEnabled(False)
        self.textedit.textChanged.connect(self.textChanged)

        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)

    def textChanged(self):
        self.dirty=True

    def newText(self):
        print("newText() Unimplemented", file=sys.stderr)
        QMessageBox.critical(None, translations["error_unimplemented"],
                                translations["error_unimplemented"])

    def openTextNarc(self, f):
        self.fname = os.path.join(
            config.project["directory"],
            "fs",
            files[config.project["versioninfo"][0]][f]
            )
        self.narc = narc.NARC(open(self.fname, "rb").read())
        self.textfilelist.clear()
        for i in range(self.narc.btaf.getEntryNum()):
            self.textfilelist.addItem(str(i))
        self.openText(0)

    def openText(self, i):
        if self.prevfile >= 0 and self.dirty:
            self.saveText()
        self.prevfile = i
        self.currentfile = i
        self.textedit.setEnabled(True)
        version = config.project["versioninfo"]
        if pokeversion.gens[version[0]] == 4:
            text = txt.gen4get(self.narc.gmif.files[self.currentfile])
        elif pokeversion.gens[version[0]] == 5:
            text = txt.gen5get(self.narc.gmif.files[self.currentfile])
        buff = ""
        for entry in text:
            buff += entry[0]+": "+entry[1]+"\n\n"
        self.textedit.setText(buff.strip("\n"))
        self.dirty = False

    def saveText(self):
        version = config.project["versioninfo"]
        texts = []
        for lines in self.textedit.toPlainText().split("\n\n"):
            t = lines.split(": ", 1)
            if len(t) < 2:
                t.extend([""])
            texts.append(t)
        if pokeversion.gens[version[0]] == 4:
            self.narc.gmif.files[self.currentfile] = txt.gen4put(texts)
        elif pokeversion.gens[version[0]] == 5:
            self.narc.gmif.files[self.currentfile] = txt.gen5put(texts)
        self.narc.toFile(open(self.fname, "wb"))
        self.dirty = False

    def search(self):
        s, ok = QInputDialog.getText(None, "Search all files", "Search (Case Insensitive)")
        if not ok or not s:
            return
        s = str(s).lower()
        hits = []
        version = config.project["versioninfo"]
        for i, f in enumerate(self.narc.gmif.files):
            if pokeversion.gens[version[0]] == 4:
                texts = txt.gen4get(f)
            else:
                texts = txt.gen5get(f)
            for entry in texts:
                if s in entry[1].lower():
                    hits.append((i, entry[0], entry[1]))
        if not hits:
            QMessageBox.information(None, "Search results", "None found")
            return
        dlg = QMainWindow(config.mw)
        dlg.setWindowTitle("Search Results")
        dlg.resize(600, 400)
        wdgt = QWidget(dlg)
        scroller = QScrollArea(wdgt)
        scroller.setGeometry(QRect(0, 0, 600, 400))
        container = QWidget(scroller)
        y = 10
        for result in hits:
            label = QLabel(container)
            label.setText("[%s] %s: %s"%result)
            label.setGeometry(QRect(0, y, 580, 20))
            y += 20
        container.setGeometry(QRect(0, 0, 600, y))
        scroller.setWidget(container)
        dlg.setCentralWidget(wdgt)
        center_screen(dlg)
        dlg.show()

    def closeEvent(self, event):
        """ override parent """
        self.saveText()


def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"],
            translations["error_noromloaded"])
        return
    EditText(config.mw).show()
