#!/usr/bin/env python

"""
Input support
"""

# $Id: __init__.py 844 2009-02-19 22:41:35Z jaraco $

__all__ = ['Joystick']

import sys

platform_path = '.'.join((__name__, sys.platform))

try:
	mod = __import__(platform_path, globals(), locals(), ['Joystick'])
	Joystick = mod.Joystick
except ImportError:
	pass
