#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
      name             = "lottanzb",
      version          = "0.0.3.012",
      description      = "LottaNZB, the GTK HellaNZB front-end",
      long_description = """LottaNZB is a pyGTK front-end for HellaNZB. HellaNZB automates the downloading of Usenet files with the help of nzb-files.""",
      author           = "aVirulence",
      author_email     = "avirulence@lottanzb.org",
      url              = "http://www.lottanzb.org/",
      packages         = ["lottanzb"],
      license          = "GPL",
      zip_safe         = False,
      package_data     = { "": ["data/*.glade", "data/*.png", "po/*/LC_MESSAGES/*.po", "po/*/LC_MESSAGES/*.mo"] },
      entry_points     = { "gui_scripts" : ["lottanzb = lottanzb.lottanzb:run"]},
      data_files       = [ ('/usr/share/pixmaps', ['data/lottanzb.png']),('/usr/share/applications', ['data/lottanzb.desktop'])]
      
)
