
"""Test a full conversion"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os

from nose import plugins
from nose import tools

from core import delete_audio_files
from core import make_audio_files
from core import make_stub_config
from core import make_stub_workers

from portify import config
from portify import converter
from portify import filesystem

TOTAL = 0
def _setup():
    global TOTAL
    TOTAL = make_audio_files()
    make_stub_workers()
    make_stub_config()
    
def _teardown():
    delete_audio_files()

@plugins.attrib.attr('slow')
@tools.with_setup(_setup, _teardown)
def test_all():
    """Let's do this"""
    f = filesystem.Walker()
    for c, fname in enumerate(f.walk()):
        con = converter.Converter(fname)
        con.convert()
        tools.ok_(os.path.exists(con.destfilename))
    tools.eq_(c+1, TOTAL)
    
@plugins.attrib.attr('slow')
@tools.with_setup(_setup, _teardown)
def test_runner_call():
    """And test the runner"""
    c = config.config
    r = converter.Runner(c)
    r()
    
@plugins.attrib.attr('slow')
@tools.with_setup(_setup, _teardown)
def test_runner_run():
    """And test the runner"""
    c = config.config
    r = converter.Runner(c)
    r.run()
