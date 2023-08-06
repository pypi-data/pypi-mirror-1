#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk

from presenter.gui.mainwindow import MainWindow

def main():
    window = MainWindow()
    window.show()
    gtk.main()

if __name__ == "__main__":
    main()

