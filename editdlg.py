#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import struct

import config
import pokeversion
from language import translate
from nds import narc, txt
from nds.fmt import FormatIterator

def defaultWidget(name, size, parent):
    sb = EditWidget(EditWidget.SPINBOX, parent)
    if size == 'H':
        sb.setValues([0, 0xFFFF])
    else:
        sb.setValues([0, 0xFF])
    sb.setName(translate(name))
    return sb
    
def defaultTextWidget(section, name, parent):
    le = EditWidget(EditWidget.LINEEDIT, parent)
    le.setName(translate(name))
    return le
    
class EditWidget(QWidget):
    NONE = 0
    SPINBOX = 1
    COMBOBOX = 2
    LABEL = 3
    CHECKBOX = 4
    LINEEDIT = 5
    TEXTEDIT = 6
    TAB = 16
    def __init__(self, kind=SPINBOX, parent=None):
        super(EditWidget, self).__init__(parent)
        self.kind = kind
        self.label = QLabel(self)
        self.label.setGeometry(QRect(0, 0, 100, 20))
        self.valuer = None
        if kind == EditWidget.SPINBOX:
            self.valuer = QSpinBox(self)
            self.setValue = self.valuer.setValue
            self.getValue = self.valuer.value
            self.setValues = self.setSpinBoxValues
            QObject.connect(self.valuer,
                QtCore.SIGNAL("valueChanged(int)"), self._changed)
        elif kind == EditWidget.COMBOBOX:
            self.valuer = QComboBox(self)
            self.setValue = self.valuer.setCurrentIndex
            self.getValue = self.valuer.currentIndex
            self.setValues = self.valuer.addItems
            QObject.connect(self.valuer,
                QtCore.SIGNAL("currentIndexChanged(int)"), self._changed)
        elif kind == EditWidget.LABEL:
            self.valuer = QLabel(self)
            self.setValue = lambda x: self.valuer.setText(str(x))
            self._getValue = self.valuer.text
        elif kind == EditWidget.CHECKBOX:
            self.valuer = QCheckBox(self)
            self.setValue = self.valuer.setChecked
            self._getValue = self.valuer.isChecked
            QObject.connect(self.valuer,
                QtCore.SIGNAL("toggled(bool)"), self._changed)
            QObject.connect(self.valuer,
                QtCore.SIGNAL("stateChanged(int)"), self._changed)
        elif kind == EditWidget.LINEEDIT:
            self.valuer = QLineEdit(self)
            self.setValue = self.valuer.setText
            self.getValue = self.valuer.text
            #TODO signals
        if self.valuer != None:
            self.valuer.setGeometry(QRect(100, 0, 150, 20))
        if kind == EditWidget.TEXTEDIT:
            self.valuer = QTextEdit(self)
            self.setValue = self.valuer.setPlainText
            self.getValue = self.valuer.toPlainText
            self.valuer.setGeometry(QRect(100, 0, 200, 60))
        QMetaObject.connectSlotsByName(self)
    def setName(self, name):
        self.label.setText(name)
    def setSpinBoxValues(self, values):
        self.valuer.setMinimum(min(values))
        self.valuer.setMaximum(max(values))
    def setValue(self, value):
        self.stored = value
    def _getValue(self):
        return self.stored
    def getValue(self):
        return int(self._getValue())
    def getGeometry(self):
        if not self.valuer:
            return (self.label.geometry().width(),
                self.label.geometry().height())
        return (self.label.geometry().width()+self.valuer.geometry().width(),
            max([self.label.geometry().height(), 
                self.valuer.geometry().height()]))
    def changed(self, param1=None):
        return
    def _changed(self, param1=None):
        self.changed(param1)
        return

class EditDlg(QMainWindow):
    wintitle = "Editor"
    def __init__(self, parent=None):
        super(EditDlg, self).__init__(parent)
        self.dirty = False
        self.currentchoice = 0
        game = config.project["versioninfo"][0]
        self.textfname = config.project["directory"]+"fs"+pokeversion.textfiles[
            game]["Main"]
        self.textnarc = narc.NARC(open(self.textfname, "rb").read())
        if pokeversion.gens[game] == 4:
            self.gettext = txt.gen4get
        elif pokeversion.gens[game] == 5:
            self.gettext = txt.gen5get
        self.setupUi()
    def setupUi(self):
        self.setObjectName("EditDlg")
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translate("menu_file"))
        self.menutasks = []
        self.addMenuEntry("file", translate("menu_new"), self.new)
        self.addMenuEntry("file", translate("menu_save"), self.save)
        self.addMenuEntry("file", translate("menu_close"), self.quit)
        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.chooser = QComboBox(self.widgetcontainer)
        self.chooser.setGeometry(QRect(50, 25, 200, 20))
        QObject.connect(self.chooser,
            QtCore.SIGNAL("currentIndexChanged(int)"), self.openChoice)
        self.currentLabel = QLabel(self.widgetcontainer)
        self.currentLabel.setGeometry(QRect(260, 25, 100, 20))
        self.tabcontainer = QTabWidget(self.widgetcontainer)
        self.tabcontainer.setGeometry(QRect(25, 50, 550, 300))
        self.tabs = []
        self.texttabs = []
        self.manualtabs = []
        self.setCentralWidget(self.widgetcontainer)
        self.updateWindowTitle("No file loaded")
        QMetaObject.connectSlotsByName(self)
    def openChoice(self, i):
        self.currentchoice = i
        self.currentLabel.setText("File ID: %i"%i)
        for tab in self.tabs:
            f = tab[0].gmif.files[i]
            fmt = tab[2]
            fields = tab[3]
            data = list(struct.unpack_from(fmt[0], f))
            for w in fields:
                w.setValue(data.pop(0))
        textcache = {}
        for tab in self.texttabs:
            getEntry = tab[1]
            for field in tab[0]:
                section = field[0]
                name = field[1]
                w = field[2]
                f, idx = getEntry(section, name, i)
                if f not in textcache:
                    textcache[f] = self.gettext(self.textnarc.gmif.files[f])
                for t in textcache[f]:
                    if idx == t[0]:
                        w.setValue(t[1])
                        break
        self.dirty = False
        self.updateWindowTitle()
    def save(self):
        if not self.dirty:
            return
        for tab in self.tabs:
            fmt = tab[2]
            fields = tab[3]
            args = []
            for w in fields:
                args.append(w.getValue())
            data = struct.pack(fmt[0], *args)
            tab[0].gmif.files[self.currentchoice] = data
            tab[0].toFile(open(tab[1], "wb"))
        self.dirty = False
        self.updateWindowTitle()
    def new(self):
        print("new() not implemented")
    def quit(self):
        if not self.checkClean():
            return
        self.close()
    def closeEvent(self, event):
        if not self.checkClean():
            event.ignore()
        event.accept()
    def checkClean(self, allowCancel=True):
        if self.dirty:
            if allowCancel:
                prompt = QMessageBox.question(self, "Close?", 
                    "This file has been modified.\n"+
                        "Do you want to save this file?",
                    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
                if prompt == QMessageBox.Cancel:
                    return False
            else:
                prompt = QMessageBox.question(self, "Close?", 
                    "This file has been modified.\n"+
                        "Do you want to save this file?",
                    QMessageBox.Yes, QMessageBox.No)
            if prompt == QMessageBox.Yes:
                if not self.save():
                    return False
        return True
    def changed(self, param1=None):
        self.dirty = True
        self.updateWindowTitle()
    def updateWindowTitle(self, text=None):
        if self.dirty:
            dirt = " [modified]"
        else:
            dirt = ""
        if not text:
            text = self.chooser.currentText()
        self.setWindowTitle("%s%s - %s - PPRE"%(text, dirt, self.wintitle))
    def addMenuEntry(self, menuname, text, callback):
        action = QAction(self.menus[menuname])
        action.setText(text)
        self.menus[menuname].addAction(action)
        self.menutasks.append(action)
        QObject.connect(action, QtCore.SIGNAL("triggered()"), callback)
    def addEditableTab(self, tabname, fmt, boundfile, getwidget=defaultWidget):
        boundnarc = narc.NARC(open(boundfile, "rb").read())
        tabscroller = QScrollArea(self.tabcontainer)
        container = QWidget(tabscroller)
        fields = []
        y = 10
        my = y
        ypadding = 0
        x = 5
        self.tabcontainer.addTab(tabscroller, tabname)
        halfguess = struct.calcsize(fmt[0][:len(fmt[0])/2])
        for i, f in enumerate(FormatIterator(fmt[0])):
            w = getwidget(fmt[i+1][0], f, container)
            if i == halfguess:
                x = width+10
                my = y
                y = 10
            if w.kind == EditWidget.TAB:
                scr = QScrollArea(self.tabcontainer)
                scr.setWidget(w)
                self.tabcontainer.addTab(scr, w.tabname)
                w.changed = self.changed
                fields.append(w)
                continue
            width, height = w.getGeometry()
            w.setGeometry(QRect(x, y, width, height))
            w.changed = self.changed
            fields.append(w)
            y += ypadding + height
        container.setGeometry(QRect(0, 0, width*2+20, max(my, y)))
        tabscroller.setWidget(container)
        self.tabs.append([boundnarc, boundfile, fmt, fields, container])
    def addTextTab(self, tabname, getEntryList, getEntry, getwidget=defaultTextWidget):
        tabscroller = QScrollArea(self.tabcontainer)
        container = QWidget(tabscroller)
        fields = []
        y = 10
        ypadding = 0
        x = 5
        mwidth = 0
        self.tabcontainer.addTab(tabscroller, tabname)
        for section in getEntryList():
            w = QLabel(translate(section[0]), container)
            w.setGeometry(QRect(x, y, 100, 20))
            y += ypadding + 20
            for entry in section[1]:
                w = getwidget(section[0], entry, container)
                width, height = w.getGeometry()
                w.setGeometry(QRect(x, y, width, height))
                w.changed = self.changed
                fields.append([section[0], entry, w])
                y += ypadding + height
                mwidth = max(mwidth, width)
        container.setGeometry(QRect(0, 0, mwidth+20, y))
        tabscroller.setWidget(container)
        self.texttabs.append([fields, getEntry, container])
        
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = EditDlg(None)
    mw.show()
    app.exec_()