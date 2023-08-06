
# $Id: amenukit.py 10 2009-10-08 18:52:20Z pytrash $

checkVars = {}
radioVars = {}

menuItems = []

def itemMethods(*args):
    for f in args:
        setattr(Item, f.__name__, f)

class Item(object):

    def __init__(self, label, command, kws):

        self.kind = self.__class__.__name__

        self._underline(label)

        self.command = command

        if kws is None:
            kws = {}
        self.kws = kws

        self.parent = None
        self.menu = None
        self.guiItem = None
        self.guiMenu = None

        if 'name' in kws:
            self.name = kws['name']
            del kws['name']

        self.name = self.label
        self.group = None

        menuItems.append(self)

    def __repr__(self):
        return '<%s  "%s">'%(self.kind, self.label)

    def copy(self):
        return self.__class__(self.label, self.command, self.kws)

    def set(self, state, loop=True):
        self.getVar().set(state, loop)

    def get(self):
        return self.getVar().get()

    def threadTree(self, parent=None):
        self.parent = parent
        self.guiCreate()


class Menu(Item):

    def __init__(self, label, menu=None, kws=None):
        Item.__init__(self, label, None, kws)
        if menu is None:
            menu = []
        self.menu = menu

    def copy(self):
        newMenu = self.__class__(self.label, None , self.kws)
        for item in self.menu:
            self.append(item.copy)

    def threadTree(self, parent=None):
        self.parent = parent
        self.guiCreate()
        if self.menu:
            for item in self.menu:
                item.threadTree(self)

class MenuBar(Item):

    def __init__(self, label, menu, kws):
        Item.__init__(self, label, None, kws)


class Command(Item):

    def __init__(self, label, command, kws=None):
        Item.__init__(self, label, command, kws)

    def doCommand(self, *args, **kw):
        print 'doCommand: [%s] for %s'% (self.command, self)


class Check(Item):

    def __init__(self, label, command, kws=None):
        Item.__init__(self, label, command, kws)

        if self.name not in checkVars:
            checkVars[self.name] = CheckVar(self.name)

    def getVar(self):
        return checkVars[self.name]


class Radio(Item):

    def __init__(self, label, command, group, kws=None):
        Item.__init__(self, label, command, kws)
        self.group = group

        if self.group not in radioVars:
            radioVars[self.group] = RadioVar(self.group)

    def getVar(self):
        return radioVars[self.group]

    def copy(self):
        return self.__class__(self.label, self.command, self.group, self.kws)


class Separator(Item):

    def __init__(self, label='', kws=None):
        Item.__init__(self, label, '', kws)


class PlaceHolder(Item):

    def __init__(self, label='', kws=None):
        Item.__init__(self, label, '', kws)

    def guiCreate(self):
        pass


class Var(object):

    def __init__(self, name):

        self.name = name
        self.mutex = None
        self._state = None

    def __repr__(self):
        return '<%s %s>'%(self.__class__.__name__, self._state)

    def get(self):
        return self._state

class CheckVar(Var):

    def set(self, state=True, loop=True):
        self._state = bool(state)
        if not loop: return
        for item in getByName(self.name, Check):
            item.guiSet(state)


class RadioVar(Var):

    def set(self, state, loop=True):
        self._state = state
        if not loop: return
        self.mutex = True
        try:
            for item in getByGroup(self.name, Radio):
                item.guiSet(item.name == self._state)
        finally:
            self.mutex = False


#########################

def getByClass(klass=Item):
    return [ item for item in menuItems if isinstance(item, klass)]

def getByName( name, klass=Item):
    items = getByClass(klass)
    return [ item for item in items if item.name == name ]

def getByGroup(group, klass=Item):
    items = getByClass(klass)
    return [item for item in items if item.group == group]

def getVar(name):
    if name in checkVars:
        return checkVars[name]
    if name in radioVars:
        return radioVars[name]
    return None

def parseMenuItem(context, item):
    klass = item[0]

    if klass == 'Menu':
        if len(item) == 3:
            label, menu = item[1:]
            kws = None
        else:
            label, menu, kws = item[1:]
        return context[klass](label, [parseMenuItem(context, i) for i in menu], kws)

    return context[klass](*item[1:])



