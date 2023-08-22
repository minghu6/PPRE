#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from editdlg import EditDlg, EditWidget, center_screen

import config
from language import translate, translations
import pokeversion
from nds import narc, txt
from nds.fmt import movedatafmt

files = pokeversion.movefiles

class EditMoves(EditDlg):
    wintitle = "Move Editor"
    def __init__(self, parent=None):
        super(EditMoves, self).__init__(parent)
        game = config.project["versioninfo"][0]
        self.wazafname = join(
            config.project["directory"],
            "fs",
            files[game]["Moves"]
            )
        self.textfname = join(
            config.project["directory"],
            "fs",
            pokeversion.textfiles[game]["Main"]
            )
        self.textnarc = narc.NARC(open(self.textfname, "rb").read())
        self.typenames = self.getTextEntry("Types")
        self.movenames = self.getTextEntry("Moves")
        self.chooser.addItems(self.movenames)
        self.addEditableTab("General", movedatafmt[game.lower()],
            self.wazafname, self.getMoveWidget)

        center_screen(self)

    def getTextEntry(self, entry):
        version = config.project["versioninfo"]

        lang = pokeversion.langs[version[1]]
        game = pokeversion.textentries[version[0]]
        entrynum = game.get(lang, game['English'])[entry]

        if pokeversion.gens[version[0]] == 4:
            text = txt.gen4get(self.textnarc.gmif.files[entrynum])
        elif pokeversion.gens[version[0]] == 5:
            text = txt.gen5get(self.textnarc.gmif.files[entrynum])
        else:
            raise ValueError
        ret = []
        for t in text:
            ret.append(t[1])
        return ret
    def getMoveWidget(self, name, size, parent):
        choices = None
        if name == "type":
            choices = self.typenames
        elif name == "contesttype":
            choices = translate("movecontesttypes")
        elif name == "category":
            choices = translate("movecategories")
        if choices:
            cb = EditWidget(EditWidget.COMBOBOX, parent)
            cb.setValues(choices)
            cb.setName(translate(name))
            return cb
        sb = EditWidget(EditWidget.SPINBOX, parent)
        if size == 'H':
            sb.setValues([0, 0xFFFF])
        elif size == 'h':
            sb.setValues([-0x8000, 0x7FFF])
        elif size == 'b':
            sb.setValues([-0x80, 0x7F])
        else:
            sb.setValues([0, 0xFF])
        sb.setName(translate(name))
        return sb

def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"],
            translations["error_noromloaded"])
        return
    EditMoves(config.mw).show()
