# $Id: testmenus.py 10 2009-10-08 18:52:20Z pytrash $



def getMenuOne():

    return ( 'Menu', '', [
  ('Menu', '_File', [
      ('Command', '_Save', 'file-save'),
      ('Separator', ),
      ('Command', '_Quit', 'file-quit'),
  ]),

  ('Menu', '_Actions', [
      ('Check', '_Fix Cell Size', 'doFixCellSize'),
      ('Check', '_Fix Cell Size', 'doFixCellSize'),
      ('Separator', ),
      ('Menu', '_Choose Radio 1', [
          ('Radio', 'choose _me', 'doChooseMe', 'group1'),
          ('Check', '_Fix Cell Size', 'doFixCellSize'),
          ('Radio', '_no choose me', 'doNoChooseMe', 'group1'),
      ]),
      ('Separator', ),
      ('Menu', 'Cats n _Dogs', [
          ('Check', '_Fix Cell Size', 'doFixCellSize'),
          ('Radio', 'prefer _dogs', 'doPreferDogs', 'group2'),
          ('Radio', 'prefer _cats', 'doPreferCats', 'group2'),
       ]),
  ]),

  ('Menu', '_Best-1', [
      ('Radio', 'wxPython', '', 'g3'),
      ('Radio', 'GTK2', '', 'g3'),
      ('Check', '_Fix Cell Size', 'doFixCellSize'),
      ('Radio', 'Tkinter', '', 'g3'),
      ('Radio', 'PyQt', '', 'g3'),
  ]),
  ('Menu', 'Best-2', [
      ('Radio', 'wxPython', '', 'g3'),
      ('Radio', 'GTK2', '', 'g3'),
      ('Radio', 'Tkinter', '', 'g3'),
      ('Check', '_Fix Cell Size', 'doFixCellSize'),
      ('Radio', 'PyQt', '', 'g3'),
  ]),
  ('Menu', '_Help', [
      ('Command', '_About', 'help-about'),
      ('Check', '_Fix Cell Size', 'doFixCellSize'),
      ('Command', '_Online Help', 'help-website'),
  ]),
])



def getMenuTwo(klasses):

    Menu, Command, Check, Radio, Separator, PlaceHolder = klasses

    return Menu( '', [

  Menu( '_File', [
      Command( '_Save', 'file-save'),
      Separator(),
      Command( '_Quit', 'file-quit'),
  ]),

  Menu( '_Actions', [
      Check('_Fix Cell Size', 'doFixCellSize'),
      Check('_Fix Cell Size', 'doFixCellSize'),
      Separator(),
      Menu('_Choose Radio 1', [
          Radio('choose _me', 'doChooseMe', 'group1'),
          Check('_Fix Cell Size', 'doFixCellSize'),
          Radio('_no choose me', 'doNoChooseMe', 'group1'),
      ]),
      Separator(),
      Menu('Cats n _Dogs', [
          Check('_Fix Cell Size', 'doFixCellSize'),
          Radio('prefer _dogs', 'doPreferDogs', 'group2'),
          Radio('prefer _cats', 'doPreferCats', 'group2'),
       ]),
  ]),

  Menu('_Best-1', [
      Radio('wxPython', '', 'g3'),
      Radio('GTK2', '', 'g3'),
      Radio('Tkinter', '', 'g3'),
      Radio('PyQt', '', 'g3'),
  ]),
  Menu('Best-2', [
      Radio('wxPython', '', 'g3'),
      Radio('GTK2', '', 'g3'),
      Radio('Tkinter', '', 'g3'),
      Radio('PyQt', '', 'g3'),
  ]),
  Menu('_Help', [
      Command('_About', 'help-about'),
      Command('_Online Help', 'help-website'),
  ]),
])
