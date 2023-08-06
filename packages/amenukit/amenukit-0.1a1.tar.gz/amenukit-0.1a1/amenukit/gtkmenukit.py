
# $Id: gtkmenukit.py 18 2009-10-09 09:38:37Z pytrash $

import gtk
import amenukit as mk

def _underline(self, label):
    self._label = label
    s = label.split('_', 1)
    if len(s) == 2:
        self.label = s[0] + s[1]
        self.underline = len(s[0])
    else:
        self.label = s[0]
        self.underline = -1

mk.itemMethods(_underline)

class Menu(mk.Menu):

    def guiCreate(self):

        if self.parent is not None:
            self.guiMenu = m = gtk.Menu()
            self.guiItem = i = gtk.MenuItem(self._label)
            i.set_submenu(m)

            pm = self.parent.guiMenu
            if pm is not None:
                pm.append(i)


class Command(mk.Command):

    def guiCreate(self):
        self.guiItem = i = gtk.MenuItem(self._label)
        self.parent.guiMenu.append(i)
        i.connect("activate", self.doCommand)


class Checkable:

    def guiSet(self, checked):
        item = self.guiItem
        if item is not None:
            item.set_active(checked)

    def guiGet(self):
        item = self.guiItem
        if item is not None:
            return item.get_active()


class Check(mk.Check, Checkable):

    def guiCreate(self):

        parentMenu = self.parent.guiItem

        self.guiItem = i = gtk.CheckMenuItem(self._label)
        pm = self.parent.guiMenu
        if pm:
            pm.append(i)
        i.connect_after('activate', self.doCommand)

    def doCommand(self, *args, **kw):
        checked = self.guiGet()
        if self.get() != checked:
            self.set(checked)
            print 'doCheckCommand: [%s] for %s'% (self.get(), self)

class Radio(mk.Radio, Checkable):

    def guiCreate(self):

        parentMenu = self.parent.guiItem

        self.guiItem = i = gtk.CheckMenuItem(self.label)
        i.set_draw_as_radio(True)

        pm = self.parent.guiMenu
        if pm:
            pm.append(i)
        i.connect('activate', self.doCommand)


    def doCommand(self, *args, **kw):

        if not self.getVar().mutex:
            self.set(self.name)
            print 'doRadioCommand: [%s] for %s'% (self.get(), self)


class Separator(mk.Separator):

    def guiCreate(self):

        self.guiItem = i = gtk.SeparatorMenuItem()
        pm = self.parent.guiMenu
        if pm is not None:
            pm.append(i)

PlaceHolder = mk.PlaceHolder

def parseMenuItem(item):
    return mk.parseMenuItem(globals(), item)

klasses = [Menu, Command, Check, Radio, Separator, PlaceHolder]
###################################

if 1:
    class gtkDemo(gtk.Window):

        def __init__(self):

            super(gtkDemo, self).__init__()

            self.set_title("gtkMenuKit")
            self.set_size_request(250, 200)

            mb = gtk.MenuBar()

            from testmenus import getMenuOne, getMenuTwo
            if 0:
                mainMenu = parseMenuItem(getMenuOne())
            else:
                mainMenu = getMenuTwo(klasses)

            mainMenu.guiMenu = mb

            mainMenu.threadTree()

            vbox = gtk.VBox(False, 2)
            vbox.pack_start(mb, False, False, 0)

            self.add(vbox)

            self.connect("destroy", gtk.main_quit)
            self.show_all()

    def doDemo():
        gtkDemo()
        gtk.main()

if __name__ == "__main__":
    doDemo()

