#!/usr/bin/env python
# $Id: weldedtetrasticks4x4.py 2 2006-08-07 19:47:13Z goodger $

"""
4 solutions (perfect solutions, i.e. no pieces cross)
"""

from puzzler import puzzles, core

core.solver((puzzles.WeldedTetraSticks4x4Matrix(),))
