#!/usr/bin/env python
import paths
from prefs import Prefs
import firstrun, gui
import gtk
import sys
import shutil
import logging
import locale, gettext

locale.setlocale(locale.LC_ALL, "")
gtk.glade.bindtextdomain("lottanzb", paths.localeDir())
gtk.glade.textdomain("lottanzb")

gettext.bindtextdomain("lottanzb", paths.localeDir())
gettext.textdomain("lottanzb")
gettext.install("lottanzb", paths.localeDir(), unicode=1)

logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

class Lotta:
    def __init__(self):
        if not Prefs.lotta.loaded:
            logging.info(_("The LottaNZB configuration could not be found. Starting configuration assistant."))
            
            self.assistant = firstrun.Assistant(True)
            gtk.main()
        
        if not Prefs.lotta["frontend_mode"] and not Prefs.hella.loaded:
            Prefs.hella.load()
        
        self.gui = gui.GUI()
        self.gui.start()
        gtk.main()

def run():
    Lotta()

if __name__ == "__main__":
    run()
