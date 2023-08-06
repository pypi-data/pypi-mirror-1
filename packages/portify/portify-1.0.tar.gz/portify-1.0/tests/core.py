
"""Core components for our tests."""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os
import shutil
import sys

from ConfigParser import ConfigParser

from portify import config
from portify import workers

from workerdefn import flacbase
from workerdefn import mp3base
from workerdefn import oggbase

pyver = sys.version_info
if pyver[1] > 5:
    from utils26 import *
else:
    from  utils25 import *
    
def make_stub_workers():
    for defn in [mp3base, flacbase, oggbase]:
        w = workers.Worker(**defn)
        workers.registry.register(w)
        
def make_stub_config():
    cwd = os.path.dirname(os.path.realpath(__file__))
    class Foo:
        pass
    c = Foo()
    c.source = '%s/Input' % (cwd,)
    c.destination = '%s/Output' % (cwd,)
    c.outputformat = 'mp3'
    c.playableformats = ['mp3',]
    c.copyexts = ['jpg', 'png', 'jpeg', 'jpe', 'gif', 'bmp',]
    c.logger = MockLogger()
    config.config = c
    
class MockLogger(object):
    
    def __init__(self):
        self.messages = []
        
    def clear(self):
        self.messages = []
        
    def _msg(self, message):
        self.messages.append(message)
        print message
        
    def info(self, message):
        self._msg("INFO: %s" % (message,))
        
    def error(self, message):
        self._msg("ERROR: %s" % (message,))
        
    def warn(self, message):
        self._msg("WARN: %s" % (message,))
        
    def debug(self, message):
        self._msg("DEBUG: %s" % (message,))
        
        
def copyfiles(filetype):
    cwd = os.path.dirname(os.path.realpath(__file__))
    source = "%s/Source/test.%s" % (cwd, filetype)
    dst = "%s/Input/%s" % (cwd, filetype)
    os.makedirs(dst)
    for c, name in enumerate([ '%02d - artist - track title' % (n,) for n in range(1,11) ]):
        destination = "%s/%s.%s" % (dst, name, filetype)
        shutil.copy(source, destination)
    if filetype == 'flac':
        shutil.copy('%s/Source/front.jpg' % (cwd,), '%s/Input/flac/front.jpg' % (cwd,))
        c = c + 1
    return c + 1
        
def make_audio_files():
    """Create the directory structures needed, and copy the test data into them"""
    total = 0
    for ft in ['flac', 'ogg', 'mp3']:
        c = copyfiles(ft)
        total = total + c
    cwd = os.path.dirname(os.path.realpath(__file__))
    os.makedirs("%s/Output" % (cwd,))
    return total

def delete_audio_files():
    """remove the test directory structures"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    shutil.rmtree("%s/Input" % (cwd,))
    shutil.rmtree("%s/Output" % (cwd,))

def make_single_output():
    """Make the output directory for the single conversion tests"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    dirname = "%s/Output/flac" % (cwd,)
    os.makedirs(dirname)
    
def delete_single_output():
    cwd = os.path.dirname(os.path.realpath(__file__))
    dirname = "%s/Output/flac" % (cwd,)
    shutil.rmtree(dirname)

    