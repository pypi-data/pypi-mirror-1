#! /usr/bin/env python
# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import sys
version = sys.version_info[:2]

MAX_SYMBOL = 333

import eecommon
import eexcept

import __builtin__

for name in dir(eexcept):
    if not name.startswith("__"):
        __builtin__.__dict__[name] = getattr(eexcept, name)

new_langlet     = eecommon.new_langlet
run             = eecommon.run
create_console  = eecommon.create_console
run_module      = eecommon.run_module


