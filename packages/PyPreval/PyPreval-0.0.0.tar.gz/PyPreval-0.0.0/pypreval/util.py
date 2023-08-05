#!/usr/bin/env python2.4
#
# (c) 2008 Andreas Kostyrka
#
"""
the popular utility collector module. Enjoy.
"""

import os, errno

def optional_makedirs(path):
    "create all needed directories, ignore EEXIST errors."
    try:
        os.makedirs(path)
    except os.error, exception:
        if exception.errno != errno.EEXIST:
            raise
