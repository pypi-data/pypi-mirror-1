
# amenukit's setup.py

# $Id: setup.py 20 2009-10-09 10:20:28Z pytrash $

from distutils.core import setup
setup(
    name = "amenukit",
    packages = ['amenukit'],
    version = "0.1a1",
    scripts=['scripts/amenukit-demo'],
    description = "Cross gui-menu building utility.",
    author = "Robert Ledger",
    author_email = "robert@pytrash.co.uk",
    url = "http://amenukit.sourceforge.net/",
    download_url = "http://sourceforge.net/projects/amenukit/files/amenukit-0.1a1.tar.gz",
    keywords = ["menu"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Software Development :: User Interfaces"
    ],
    long_description = """\
Gui independent meunu system.
-----------------------------

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

"""
)
