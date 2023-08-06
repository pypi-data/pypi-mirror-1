
# $Id: qtmenukit.py 18 2009-10-09 09:38:37Z pytrash $
from PyQt4 import QtGui, QtCore
import amenukit as mk

def _underline(self, label):
    s = label.split('_', 1)
    if len(s) == 2:
        self.label = s[0] + s[1]
        self._label = s[0] + '&' + s[1]
        self.underline = len(s[0])
    else:
        self.label = s[0]
        self._label = s[0]
        self.underline = -1

def _bind(self):
   self.guiItem.connect(self.guiItem, QtCore.SIGNAL('triggered()'), self.doCommand)

mk.itemMethods(_underline, _bind)


class Menu(mk.Menu):

    def guiCreate(self):
        if self.parent is not None:
            pm = self.parent.guiMenu
            if pm is not None:
                self.guiMenu = pm.addMenu(self._label)


class Command(mk.Command):

    def guiCreate(self):
        if self.parent and self.parent.guiMenu:
            self.guiItem = self.parent.guiMenu.addAction(self._label)
            self._bind()

class Checkable:

    def guiSet(self, checked):
        item = self.guiItem
        if item is not None:
            item.setChecked(checked)

    def guiGet(self):
        item = self.guiItem
        if item is not None:
            return item.isChecked()


class Check(mk.Check, Checkable):

    def guiCreate(self):
        if self.parent and self.parent.guiMenu:
            self.guiItem = self.parent.guiMenu.addAction(self._label)
            self.guiItem.setCheckable(True)
            self._bind()

    def doCommand(self, *args, **kw):
        self.set(self.guiGet())
        print 'doCheck: [%s] for %s'% (self.get(), self)


class Radio(mk.Radio, Checkable):

    def guiCreate(self):
        if self.parent and self.parent.guiMenu:
            self.guiItem = self.parent.guiMenu.addAction(self._label)
            self.guiItem.setCheckable(True)
            QtGui.QActionGroup(self.parent.guiMenu).addAction(self.guiItem)
            self._bind()

    def doCommand(self, *args, **kw):
        if self.guiGet():
            self.set(self.name)
            print 'doRadio: [%s] for %s'% (self.get(), self)


class Separator(mk.Separator):

    def guiCreate(self):
        if self.parent is not None:
            pm = self.parent.guiMenu
            if pm is not None:
                self.guiMenu = pm.addSeparator()


PlaceHolder = mk.PlaceHolder

def parseMenuItem(item):
    return mk.parseMenuItem(globals(), item)

klasses = [Menu, Command, Check, Radio, Separator, PlaceHolder]
###################################
if 1:

    import sys

    class qtDemo(QtGui.QMainWindow):

        def __init__(self):

            QtGui.QMainWindow.__init__(self)
            self.setWindowTitle('qtMenuKit')

            mb = self.menuBar()

            from testmenus import getMenuOne, getMenuTwo
            if 0:
                mainMenu = parseMenuItem(getMenuOne())
            else:
                mainMenu = getMenuTwo(klasses)

            mainMenu.guiMenu = mb
            mainMenu.threadTree()

    def doDemo():
        app = QtGui.QApplication(sys.argv)
        main = qtDemo()
        main.show()
        app.exec_()

if __name__ == "__main__":
    doDemo()
