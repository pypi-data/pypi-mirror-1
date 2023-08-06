#!/usr/bin/env python
"""\
Python documentation sidebar generator
Copyright (C) 2008 Remy Blank
"""
# This file is part of Sydebar.
# 
# This program is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the 
# Free Software Foundation, version 2. A copy of the license is provided 
# in the file COPYING.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
# Public License for more details.

from os.path import basename, dirname, isfile, join, realpath
import sys

if __name__ == "__main__":
    if "__file__" in dir():
        # Prepend distribution library path if present
        distPath = dirname(dirname(realpath(__file__)))
        if isfile(join(distPath, "setup.py")):
            sys.path.insert(0, join(distPath, "lib"))

    try:
        from Sydebar import main
    except ImportError:
        if "--debug" in sys.argv:
            raise
        sys.stderr.write("%s: Cannot find Sydebar library (check your PYTHONPATH)\n" % basename(sys.argv[0]))
        sys.exit(99)

    sys.exit(main(sys.argv, sys.stdout, sys.stderr))
