#! /usr/bin/env python
# URL:     http://www.fiber-space.de
# Author:  Kay Schluehr <easyextend@fiber-space.de>
# Date:    10 May 2006

import sys
version = sys.version_info[:2]

MAX_SYMBOL = 333

import eecommon
from  eexcept import*

__dev__ = False  # global development flag

new_fiber      = eecommon.new_fiber
run            = eecommon.run
create_console = eecommon.create_console
run_module     = eecommon.run_module
