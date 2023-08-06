#!/usr/bin/env python

# pdock setup file

from distutils.core import setup

setup(name='pdock',
      version='0.1.1',
      description='an experimental docking implementation',
      author='Andi Albrecht',
      author_email='albrecht.andi@gmail.com',
      url='http://code.google.com/p/python-pocdock/',
      download_url='http://code.google.com/p/python-pocdock/downloads/list',
      packages = ['pdock'],
      license = 'GPL',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
      ],
      long_description = '''
pocdock is an experimental PyGTK docking implementation.

**Example usage**::

    import gtk
    import pdock
    
    win = gtk.Window()
    dock = pdock.Dock()
    win.add(dock)
    dock.add_item("item1", gtk.TextView(), "First item", "gtk-ok")
    dock.add_item("item2", gtk.TextView(), "Second item", "gtk-apply")
    win.show_all()
    
    gtk.main()

**Screenshots**

To see it in action, have a look at CrunchyFrog's screenshots
(http://cf.andialbrecht.de/screenshots.html).
'''
)
