#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple utilties for Plone product initilisation and installation.

This library originated from a desire to do away with the large amount of
boilerplater code required to bootstrap a Plone product. It provides
installer, deinstaller and initaliser classes that provide reasonable default
behaviour. It uses the old (Plone 2.x) way of installing old-fashioned
Products but these are still surprisingly common in these days of egg-ified
Plone add-ons (and sometimes easier to write). It won't fit all purposes but
does make for quick-and-dirty bootstrapping of a Product.

It also includes some other useful utility functions for Plone, mostly with
a eye towards manipulating Plone from the debug prompt.

There are numerous other Products or package that provide similar (and
arguably better) functionality, including InstallUtils and PloneUtils.

"""

__docformat__ = 'restructuredtext en'
__author__ = "P-M Agapow <agapow@bbsrc.ac.uk>"
__version__ = "0.3"


### IMPORTS ###

### IMPLEMENTATION ###

### TEST & DEBUG ###

def _doctest ():
   import doctest
   doctest.testmod ()


### MAIN ###

if __name__ == '__main__':
   _doctest()


### END #####################################################################