#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup

setup(name         = "grun",
      version      = "0.1",
      description  = "The simplest GUI builder (tk/gtk), for RAD scripts",
      author       = "manatlan",
      author_email = "manatlan@gmail.com",
      url          = "http://www.manatlan.com/page/grun",
      packages   = ["grun","grun/gui"],
      data_files=[],
      license      = "PSF",
      #~ requires     = ["pygtk","tkinter","pynotify","xdg"],
      classifiers  = [
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        ],
      long_description=file("README.txt").read(),
     )
