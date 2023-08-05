#!/usr/bin/env python

# $Id: setup.py,v 1.9 2004/03/04 17:29:18 jribbens Exp $

from distutils.core import setup

setup(name="jonpy",
      version="0.06",
      description="Jon's Python modules",
      author="Jon Ribbens",
      author_email="jon+jonpy@unequivocal.co.uk",
      url="http://jonpy.sourceforge.net/",
      packages=['jon', 'jon.wt']
)
