#!/usr/bin/env python
# $Id: pentominoes5x12.py 2 2006-08-07 19:47:13Z goodger $

"""
1010 solutions
"""

from puzzler import puzzles, core

core.solver((puzzles.Pentominoes5x12MatrixA(),
             puzzles.Pentominoes5x12MatrixB(),))
