#!/usr/bin/env python

# $Id: ui.py 765 2009-01-31 22:26:25Z jaraco $

import ctypes
from jaraco.windows.util import ensure_unicode

def MessageBox(text, caption=None, handle=None, type=None):
	text, caption = map(ensure_unicode, (text, caption))
	ctypes.windll.user32.MessageBoxW(handle, text, caption, type)
