
"""Test directory walking"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os
import shutil
import time

from nose import tools

from core import delete_audio_files
from core import delete_single_output
from core import make_audio_files
from core import make_single_output
from core import make_stub_config
from core import make_stub_workers
from core import touch

from portify import config
from portify import filesystem

TOTAL = 0

def setup():
    global TOTAL
    TOTAL = make_audio_files()
    make_stub_workers()
    make_stub_config()
    
def teardown():
    delete_audio_files()
    
def test_basic():
    """Our first test.  Really ought to pass"""
    print "I am test"
    pass

def test_no_preexisting():
    """Test that we get the right number of files when no converted files
    are pre-existing"""
    w = filesystem.Walker()
    tools.eq_(TOTAL, len(list(w.walk())))
    
def test_makeoutputfilename():
    """Test that we get the right destination filename"""
    c = config.config
    srcfile = "%s/flac/01 - artist - test title.flac" % (c.source,)
    destfile = "%s/flac/01 - artist - test title.%s" % (c.destination, c.outputformat)
    w = filesystem.Walker()
    tools.eq_(destfile, w.makeoutputfilename(srcfile))

@tools.with_setup(make_single_output, delete_single_output)
def test_some_preexisting():
    """Create some files after the base files are created - they're newer,
    so they shouldn't be converted"""
    w = filesystem.Walker()
    cwd = os.path.dirname(os.path.realpath(__file__))
    source = "%s/Source/test.mp3" % (cwd,)
    for c, name in enumerate([ '%02d - artist - track title.mp3' % (n,) for n in range(1,9) ]):
        destination = "%s/Output/flac/%s" % (cwd, name)
        shutil.copy(source, destination)
    shutil.copy("%s/Source/front.jpg" % (cwd,), "%s/Output/flac/front.jpg" % (cwd,))
    sub = c + 2
    tools.eq_(TOTAL - sub, len(list(w.walk())))
    
@tools.with_setup(make_single_output, delete_single_output)
def test_preexisting_but_older():
    """Create some files *before* the base files are created - they're
    older, so they should be converted"""
    w = filesystem.Walker()
    cwd = os.path.dirname(os.path.realpath(__file__))
    source = "%s/Source/test.mp3" % (cwd,)
    st = os.stat(source)
    for n in range(1,9):
        destfile = '%s/Output/flac/%02d - artist - track title.mp3' % (cwd,n)
        shutil.copy(source, destfile)
        touch(destfile, (st.st_atime, st.st_mtime))
    tools.eq_(TOTAL, len(list(w.walk())))

@tools.with_setup(make_single_output, delete_single_output)
def test_unrecognised_formats():
    """Create some files of the wrong format"""
    c = config.config
    w = filesystem.Walker(c.source, c.destination, c.outputformat)
    cwd = os.path.dirname(os.path.realpath(__file__))
    source = "%s/Source/test.mp3" % (cwd,)
    for n in range(1,9):
        destfile = '%s/Input/flac/%02d - artist - track title.madeup' % (cwd,n)
        shutil.copy(source, destfile)
    tools.eq_(TOTAL, len(list(w.walk())))

