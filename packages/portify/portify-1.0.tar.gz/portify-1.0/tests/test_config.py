
"""Test config"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import logging
import os

from ConfigParser import ConfigParser

from nose import tools

from portify import config
from portify import workers

def setup():
    pass

def teardown():
    cwd = os.path.dirname(os.path.realpath(__file__))
    logfile = "%s/portify.log" % (cwd,)
    if os.path.exists(logfile):
        os.unlink(logfile)
    del workers.registry
    workers.registry = workers.Registry()
        
def test_basic():
    """Our first test.  Really ought to pass"""
    print "I am test"
    pass

def test_mainsections():
    """Read the main sections of a config file"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    expected = {
        'source': '/var/local/music',
        'destination': '/var/local/portable',
        'outputformat': 'mp3',
        'playableformats': ['ogg', 'mp3'],
        }
    fname = "%s/Source/noworkers.conf" % (cwd,)
    c = config.Config(fname, verbose=False, logdir=cwd)
    for k, v in expected.items():
        tools.eq_(getattr(c, k), v)
        
def test_registerworkers():
    """Open a full config file, with workers and everything"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    fname = "%s/Source/complete.conf" % (cwd,)
    c = config.Config(fname, verbose=False, logdir=cwd)
    r = workers.registry
    tools.eq_(len(r.allworkers()), 4)

def test_loggerattributes():
    """Test that the logger is as defined"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    fname = "%s/Source/noworkers.conf" % (cwd,)
    c = config.Config(fname, verbose=False, logdir=cwd)
    tools.eq_('portify', c.logger.name)
    tools.eq_(logging.ERROR, c.logger.level)
    
    