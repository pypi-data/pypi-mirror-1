import Tkinter as tk

# $Id: tkmenukit.py 18 2009-10-09 09:38:37Z pytrash $
import amenukit as mk

tkRadioGroups = {}
tkCheckVars = {}


def _underline(self, label):
    s = label.split('_', 1)
    if len(s) == 2:
        self.label = self._label = s[0] + s[1]
        self.underline = len(s[0])
    else:
        self.label = self._label = label
        self.underline = -1

mk.itemMethods(_underline)


class Menu(mk.Menu):

    def guiCreate(self):

        if self.parent is None:
            self.guiItem = tk.Menu(self.guiItem)
        else:
            parentMenu = self.parent.guiItem
            self.guiItem = m = tk.Menu(parentMenu)

            kw = {}
            if self.underline >=0:
                kw['underline'] = self.underline
            parentMenu.add_cascade(label=self._label, menu=m, **kw)


class Command(mk.Command):

    def guiCreate(self):
        add = self.parent.guiItem.add_command
        kw = {}
        if self.underline >=0:
            kw['underline'] = self.underline
        add(label=self._label, command=self.doCommand, **kw)

class Checkable:
    pass

class Check(mk.Check, Checkable):

    def guiCreate(self):
        parentMenu = self.parent.guiItem

        if self.name not in tkCheckVars:
            tkCheckVars[self.name] = tk.IntVar()

        kw = {}
        if self.underline >=0:
            kw['underline'] = self.underline

        parentMenu.add_checkbutton(
            label=self._label,
            variable=tkCheckVars[self.name],
            command=self.doCommand,
            **kw
        )

    def guiGet(self):
        return tkCheckVars[self.name].get()

    def guiSet(self, checked):
        tkCheckVars[self.name].set(checked)

    def doCommand(self):
        self.set(not self.get())
        print 'doCheckCommand: [%s] for %s'% (self.get(), self)


class Radio(mk.Radio, Checkable):


    def guiCreate(self):
        parentMenu = self.parent.guiItem

        if self.group not in tkRadioGroups:
            tkRadioGroups[self.group] = tk.StringVar()

        kw = {}
        if self.underline >=0:
            kw['underline'] = self.underline
        var = tkRadioGroups[self.group]
        parentMenu.add_radiobutton(
            label=self._label,
            variable=var,
            value=self.name,
            command=self.doCommand,
            **kw
        )

    def guiGet(self):
        tkRadioGroups[self.group].get()

    def guiSet(self, checked):
        tkRadioGroups[self.group].set(checked)

    def doCommand(self):
        self.set(self.name, loop=False)
        print 'doRadioCommand: [%s] for %s'%(self.get(), self)


class Separator(mk.Separator):

    def guiCreate(self):
        self.parent.guiItem.add_separator()

    def doCommand(self):
        pass

PlaceHolder = mk.PlaceHolder

def parseMenuItem(item):
    return mk.parseMenuItem(globals(), item)

klasses = [Menu, Command, Check, Radio, Separator, PlaceHolder]
###################################
if 1:

    def tkDemo(root):

        from testmenus import getMenuOne, getMenuTwo
        if 0:
            mainMenu = parseMenuItem(getMenuOne())
        else:
            mainMenu = getMenuTwo(klasses)

        print mainMenu

        mainMenu.guiItem = root
        mainMenu.threadTree()

        root.config(menu=mainMenu.guiItem)

    def doDemo():
        root = tk.Tk()
        root.wm_title('tkMenuKit')
        root.geometry('400x400+200+200')

        root.after(0, tkDemo, root)
        tk.mainloop()

if __name__ == "__main__":
    doDemo()
