
"""Core components for our tests."""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'


import logging
import os
import sys

from nose import tools

from portify import config

LOGFILE = 'tmplogfile.log'

def setup():
    pass

def teardown():
    logfile = logname()
    if os.path.exists(logfile):
        os.unlink(logfile)
        
def logname():
    cwd = os.path.dirname(os.path.realpath(__file__))
    return "%s/%s" % (cwd, LOGFILE)

def getlines():
    logfile = logname()
    f = open(logfile)
    lines = f.readlines()
    for line in lines:
        print line
    return len(lines)

def make_logfile():
    cwd = os.path.dirname(os.path.realpath(__file__))
    f = open('%s/%s' % (cwd, LOGFILE), 'w')
    f.close()
    
def delete_logfile():
    cwd = os.path.dirname(os.path.realpath(__file__))
    os.unlink('%s/%s' % (cwd, LOGFILE))

@tools.with_setup(make_logfile, delete_logfile)
def test_startlogger_file():
    """Does the logging system start (to file)?"""
    logfile = logname()
    config.start_logger(logfile, 'DEBUG')
    tools.eq_(getlines(), 1)
    
def test_startlogger_stderr():
    """Does the logging system start (to stderr)?"""
    logfile = logname()
    save = sys.stderr
    out = open(logfile, 'w')
    sys.stderr = out
    config.start_logger(logfile, 'DEBUG', True)
    sys.stderr = save
    tools.eq_(getlines(), 1)
    