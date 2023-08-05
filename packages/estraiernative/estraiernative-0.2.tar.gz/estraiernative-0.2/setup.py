#
# $Id: setup.py,v 1.2 2007/04/15 05:52:47 yosida Exp $
#

from distutils.core import setup, Extension

ext = Extension("_estraiernative",
                ["estraiernative.c"],
                libraries=["estraier"])
setup(name="estraiernative", version="0.2", ext_modules=[ext])
