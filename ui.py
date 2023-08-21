from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from language import translations

def addAction(menu, name, action):
    a = QAction(menu)
    a.setText("menu_"+name)
    menu.addAction(a)
