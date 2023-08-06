#!/usr/bin/python
#
# File: setup.py
#
# This file is part of the biblio-py project
#
# Copyright (C) 2009 Juan Fiol
# This is free software.  You may redistribute copies of it under the terms of
# the GNU General Public License version 2 or later.
# There is NO WARRANTY, to the extent permitted by law.
#
# Written by Juan Fiol <juanfiol@gmail.com>
import os
import glob
from distutils.core import setup
# import distutils

VERSION= '0.5.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('ChangeLog')
    + '\n'
    )

packages = ["yapbib","query_ads"]
scripts= glob.glob('scripts/*.py')

# do the distutils setup
setup(name="biblio-py",
      version = VERSION,
      description = "Package to manage bibliography files",
      long_description = long_description,
      license = "GPLv2",
      url = "http://cabcat2.cnea.gov.ar/staff/fiol/biblio-py.html",
      download_url="http://cabcat2.cnea.gov.ar/staff/fiol/biblio-py-0.5.1.tar.gz",
      keywords= "bibliography, bibtex, converter, html, xml, latex, parser",
      author = "Juan Fiol",
      author_email = "juanfiol@gmail.com",
      packages = packages,
      scripts = scripts,
      )

