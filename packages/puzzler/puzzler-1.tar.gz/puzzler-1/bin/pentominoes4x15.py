#!/usr/bin/env python
# $Id: pentominoes4x15.py 2 2006-08-07 19:47:13Z goodger $

"""
368 solutions
"""

from puzzler import puzzles, core

core.solver((puzzles.Pentominoes4x15MatrixA(),
             puzzles.Pentominoes4x15MatrixB(),))
