#!/usr/bin/env python
# $Id: tetrasticks5x5.py 2 2006-08-07 19:47:13Z goodger $

"""
1795 solutions total:

* 72 solutions omitting H
* 382 omitting J
* 607 omitting L
* 530 omitting N
* 204 omitting Y

All are perfect solutions (i.e. no pieces cross).
"""

from puzzler import puzzles, core

core.solver((puzzles.TetraSticks5x5Matrix(),))
