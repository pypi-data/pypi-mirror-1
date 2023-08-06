A Menu Kit - README
===================

Author: Robert Ledger
Email:  <robert@pytrash.co.uk>
Website: http://amenukit.sourceforge.net/

Licence: GNU Library or Lesser General Public License (LGPL)

Summary
-------

This is a Python module designed to simplify the specification, creation, and
dynamic manipulation of gui menus. Menus systems written with this module will
work without modification on all supported gui's.

The kit supplies wrappers for four common python gui's:

 - tkinter    [tkmenukit.py]
 - pygtk      [gtkmenukit.py]
 - pyqt       [qtmenukit.py]
 - wxPython   [wxmenukit.py]

Menus are represented by python objects linked together in a tree structure. The
python objects can be inactive, or active.  Active menus are connected to real
menus in the gui and changes made to the python structure will be reflected in
the gui.

Menus (and menu fragments) can be built up using normal python methods for
manipulating data structures or from lists of python strings or from data
formats such as XML, jason, yaml etc. Python menu structures, however
constructed, can be converted easily into any of these formats.

Porting a menu system from one gui to another, simply involves importing a
different wrapper module. Everything else will work exactly the same.


Download and Install
--------------------

amenukit can be downloaded and installed using one of the following methods:

1)  If you have easy_install or pip installed and are connected to the internet,
    use either:

        pip install amenukit

    or

        easy_install amenukit

    Thats it - done!

2)  Downloaded the latest tarball from:

        http://sourceforge.net/projects/amenukit/files/

    Unpack the tarball into a temporary location.

    Execute:

        python setup.py install


3)  Checkout the latest sources from the projects subversion repository.

        svn co https://amenukit.svn.sourceforge.net/svnroot/amenukit/trunk amenukit

    Execute:

        python setup.py install

$Id: README.txt 19 2009-10-09 10:13:14Z pytrash $
