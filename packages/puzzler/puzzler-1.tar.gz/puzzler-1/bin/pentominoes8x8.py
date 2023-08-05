#!/usr/bin/env python
# $Id: pentominoes8x8.py 2 2006-08-07 19:47:13Z goodger $

"""
8x8 grid with 2x2 center hole.
65 solutions
"""

from puzzler import puzzles, core

core.solver((puzzles.Pentominoes8x8CenterHoleMatrixA(),
             puzzles.Pentominoes8x8CenterHoleMatrixB(),))
