#!/usr/bin/env python

"""screencastwriter - Screencast Writer

Copyright 2006 Baiju M <baiju.m.mail@gmail.com>

This program is released under GNU GPL version 2,
or (at your option) any later version

$Id: scw.py 58 2006-03-26 17:44:25Z baijum81 $
"""

SCREAN_CAST_FILE = 'testcast.txt'

import os
import signal
import gtk
import gtk.glade

class ScreencastWriter(object):

    def __init__(self, castfile):
        self.caststrings = open(castfile).read().split("---")
        self.currentpage = -1
        self.initialiseWindow()

    def initialiseWindow(self):
        xml = gtk.glade.XML(
            os.path.join(os.path.dirname(__file__), "scw.glade"))
        self.mainwin = xml.get_widget("mainwin")
        self.notebook = xml.get_widget("notebook")
        self.label = xml.get_widget("label")
        self.textview = xml.get_widget("textview")
        self.previousbutton = xml.get_widget("previousbutton")
        self.nextbutton = xml.get_widget("nextbutton")
        self.writebutton = xml.get_widget("writebutton")

        self.mainwin.connect("delete_event", self.on_window_delete)
        self.previousbutton.connect("clicked", self.on_previousbutton_clicked)
        self.nextbutton.connect("clicked", self.on_nextbutton_clicked)
        self.writebutton.connect("clicked", self.on_writebutton_clicked)

    def on_window_delete(self, *args):
        gtk.main_quit()

    def getPreviousPage(self):
        try:
            self.caststrings[self.currentpage - 1]
        except IndexError:
            self.currentpage = -1
        else:
            self.currentpage = self.currentpage - 1
        return self.currentpage

    def getNextPage(self):
        try:
            self.caststrings[self.currentpage + 1]
        except IndexError:
            self.currentpage = 0
        else:
            self.currentpage = self.currentpage + 1
        return self.currentpage

    def on_previousbutton_clicked(self, *args):
        self.notebook.set_current_page(0)
        self.label.set_markup(self.caststrings[self.getPreviousPage()])

    def on_nextbutton_clicked(self, *args):
        self.notebook.set_current_page(0)
        self.label.set_markup(self.caststrings[self.getNextPage()])

    def on_writebutton_clicked(self, *args):
        togdict = {0: 1, 1:0}
        page = self.notebook.get_current_page()
        self.notebook.set_current_page(togdict[page])

    def main(self):
        gtk.main()
        pass


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    screencastwriter = ScreencastWriter(SCREAN_CAST_FILE)
    screencastwriter.main()
