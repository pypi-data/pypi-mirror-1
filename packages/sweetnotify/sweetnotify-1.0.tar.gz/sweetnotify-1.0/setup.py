#!/usr/bin/env python

from distutils.core import setup

setup(name='sweetnotify',
      version='1.0',
      description='A gnome desktop sweetter.net notify',
      author='danigm',
      author_email='dani@danigm.net',
      license="gplv3",
      keyword="sweetter pynotify",
      install_requires="pysweetter",
      url='http://danigm.net',
      data_files=[("/usr/local/bin/", ["sweetnotify.py"]),],
     )

