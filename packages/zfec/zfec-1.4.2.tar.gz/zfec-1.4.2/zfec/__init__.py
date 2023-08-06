"""
zfec -- fast forward error correction library with Python interface

maintainer web site: U{http://allmydata.com/source/zfec}

zfec web site: U{http://allmydata.com/source/zfec}
"""

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that hasn't run darcsver, and didn't come with a
    # _version.py, so we don't know what our version is. This should not happen
    # very often.
    pass

from _fec import Encoder, Decoder, Error
import easyfec, filefec, cmdline_zfec, cmdline_zunfec

# zfec -- fast forward error correction library with Python interface
# 
# Copyright (C) 2007 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn
# mailto:zooko@zooko.com
# 
# This file is part of zfec.
#
# See README.txt for licensing information.
