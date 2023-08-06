
# $Id: wxmenukit.py 18 2009-10-09 09:38:37Z pytrash $
import wx
import amenukit as mk

import img

wxRadioGroups = {}

def _underline(self, label):
    s = label.split('_', 1)
    if len(s) == 2:
        self.label = s[0] + s[1]
        self._label = s[0] + '&' + s[1]
        self.underline = len(s[0])
    else:
        self.label = self._label = s[0]
        self.underline = -1

def _bind(self):
    wx.GetApp().Bind(wx.EVT_MENU, self.doCommand, self.guiItem)

def wxGetIndex(self):
    lst = self.parent.guiMenu.GetMenuItems()
    i = -1
    for item in lst:
        i += 1
        if item is self.guiItem:
            return i
    return i


mk.itemMethods(_underline, _bind, wxGetIndex)

class Menu(mk.Menu):

    def guiCreate(self):
        if self.parent is not None:
            self.guiMenu = m = wx.Menu()
            pm = self.parent.guiMenu
            if pm is not None:
                try:
                    pm.AppendMenu(wx.ID_ANY, self._label, m)
                except:
                    pm.Append(m, self._label)


class Command(mk.Command):

    def guiCreate(self):
        self.guiItem = i = wx.MenuItem(None, wx.ID_ANY, self._label, kind=wx.ITEM_NORMAL)
        if self.parent and self.parent.guiMenu:
            self.parent.guiMenu.AppendItem(i)
        self._bind()


class Checkable:

    def guiSet(self, checked):
        item = self.guiItem
        if item is not None:
            item.Check(bool(checked))

    def guiGet(self):
        item = self.guiItem
        if item is None: return None
        return item.IsChecked()


class Check(mk.Check, Checkable):

    def guiCreate(self):
        self.guiItem = wx.MenuItem(
            None, wx.ID_ANY, self._label, kind=wx.ITEM_CHECK)
        self.parent.guiMenu.AppendItem(self.guiItem)
        self._bind()

    def doCommand(self, event):
        self.set(self.guiGet())
        print 'doCheckCommand: [%s] for %s'%(self.get(), self)


class Radio(mk.Radio, Checkable):


    def guiSet(self, checked):
        item = self.guiItem
        idx = self.wxGetIndex()
        self.parent.guiMenu.RemoveItem(item)

        if self.get()==self.name:
            item.SetBitmap(img.onRadio.GetBitmap())
        else:
            item.SetBitmap(img.offRadio.GetBitmap())

        self.parent.guiMenu.InsertItem(idx, item)

    def guiCreate(self):
        self.guiItem = i = wx.MenuItem(
            self.parent.guiMenu, wx.ID_ANY, self._label, kind=wx.ITEM_NORMAL)
        self.parent.guiMenu.AppendItem(i)
        self.guiSet(True)
        self._bind()

    def doCommand(self, event):
        self.set(self.name)
        print 'doRadioCommand: [%s] for %s'%(self.get(), self)


class Separator(mk.Separator):

    def guiCreate(self):
        self.guiItem = self.parent.guiMenu.AppendSeparator()


PlaceHolder = mk.PlaceHolder

def parseMenuItem(item):
    return mk.parseMenuItem(globals(), item)

klasses = [Menu, Command, Check, Radio, Separator, PlaceHolder]
###################################
if 1:

  class MyMenu(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(380, 250))

        menubar = wx.MenuBar()

        from testmenus import getMenuOne, getMenuTwo
        if 0:
            mainMenu = parseMenuItem(getMenuOne())
        else:
            mainMenu = getMenuTwo(klasses)

        mainMenu.guiMenu = menubar
        mainMenu.threadTree()

        self.SetMenuBar(menubar)
        self.Centre()


    def OnQuit(self, event):
        print 'onquit'
        self.Close()

  class MyApp(wx.App):
    def OnInit(self):
        frame = MyMenu(None, -1, 'wxMenuKit')
        frame.Show(True)
        return True

  def doDemo():
    app = MyApp(0)
    app.MainLoop()

if __name__ == "__main__":
    doDemo()
