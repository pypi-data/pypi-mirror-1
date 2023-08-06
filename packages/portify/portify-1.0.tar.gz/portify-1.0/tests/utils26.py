
"""Core components for our tests."""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os

def touch(fname, times = None):
    with file(fname, 'a'):
        os.utime(fname, times)
