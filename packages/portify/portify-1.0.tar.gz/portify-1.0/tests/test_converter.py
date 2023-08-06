
"""Test file conversion"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os
import shutil
import sys

from mutagen import easyid3
from mutagen import flac
from mutagen import oggvorbis
from nose import plugins
from nose import tools

from core import delete_audio_files
from core import delete_single_output
from core import make_audio_files
from core import make_single_output
from core import make_stub_config
from core import make_stub_workers

from portify import config
from portify import converter
from portify import workers

ARGS = [['flac', 'flac', 'flac',],
        ['ogg', 'oggvorbis', 'oggvorbis',],
        ['mp3', 'easyid3', 'mp3',],
        ]

def _setup():
    make_audio_files()
    make_stub_workers()
    make_stub_config()
    
def _teardown():
    delete_audio_files()
    
def test_basic():
    """Our first test.  Really ought to pass"""
    print "I am test"
    pass

@tools.with_setup(_setup, _teardown)
def _source(fmt, klass, title):
    expected = {
        'title': [u'A test %s' % (title,),],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        'genre': [u'Electronic',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    for name in [ '%02d - artist - track title' % (n,) for n in range(1,11) ]:
        fname = '%s/Input/%s/%s.%s' % (cwd, fmt, name, fmt)
        m = sys.modules['mutagen.%s' % (klass,)]
        f = m.Open(fname)
        for k, v in expected.items():
            tools.ok_(k in f, '%s not in %r' % (k,f))
            tools.eq_(f[k], v)

def test_sources():
    """Do the source files exist, are they of the right format and do
    they have the right tags?"""
    for args in ARGS:
        yield tuple([_source,] + args)
        
@tools.with_setup(_setup, _teardown)
def _convertertags(fmt, klass, title):
    expected = {
        'title': [u'A test %s' % (title,),],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    for name in [ '%02d - artist - track title' % (n,) for n in range(1,11) ]:
        fname = '%s/Input/%s/%s.%s' % (cwd, fmt, name, fmt)
        c = converter.Converter(fname, 'flac')
        f = c.gettags()
        for k, v in expected.items():
            tools.ok_(k in f, '%s not in %r' % (k,f))
            tools.eq_(f[k], v)
    
def test_converter_read_tags():
    """Does the converter's reading of the id3 tags agree with our own?"""
    for args in ARGS:
        yield tuple([_convertertags,] + args)
    
@tools.with_setup(_setup, _teardown)
@tools.raises(IOError)
def test_writetags_breaks():
    """Does writetags break when the dest file is not there?"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/mp3/%s.mp3' % (cwd, name)
    c = converter.Converter(fname, 'flac')
    c.writetags({})
    
@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
@plugins.attrib.attr('slow')
def test_single_stream_conversion():
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'mp3')
    c.convertaudio()
    oname = '%s/Output/flac/%s.mp3' % (cwd, name)
    tools.eq_(oname, c.destfilename)
    tools.ok_(os.path.exists(c.destfilename))

@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
@plugins.attrib.attr('slow')
def test_single_file_conversion():
    """Test a file based conversion, rather than a stream one"""
    r = workers.registry
    w = r.worker('mp3')
    oldencodestdin = w.encodestdin
    w.encodestdin = None
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'mp3')
    c.convertaudio()
    oname = '%s/Output/flac/%s.mp3' % (cwd, name)
    tools.eq_(oname, c.destfilename)
    tools.ok_(os.path.exists(c.destfilename))
    w.encodestdin = oldencodestdin
    
@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
@plugins.attrib.attr('slow')
def test_mp3_tag_conversion():
    """Test that the tags have all come across"""
    expected = {
        'title': [u'A test flac',],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'mp3')
    c.convertaudio()
    c.movetags()
    oname = '%s/Output/flac/%s.mp3' % (cwd, name)
    tools.eq_(oname, c.destfilename)
    f = easyid3.Open(oname)
    for k, v in expected.items():
        tools.eq_(v, f[k])

@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
@plugins.attrib.attr('slow')
def test_nonmp3_tag_conversion():
    """Test that the tags have all come across"""
    expected = {
        'title': [u'A test flac',],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'ogg')
    c.convertaudio()
    c.movetags()
    oname = '%s/Output/flac/%s.ogg' % (cwd, name)
    tools.eq_(oname, c.destfilename)
    f = oggvorbis.Open(oname)
    for k, v in expected.items():
        tools.eq_(v, f[k])

@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
def test_supplementaryfile():
    """Do we copy across the supplementary files"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    fname = '%s/Input/flac/front.jpg' % (cwd,)
    c = converter.Converter(fname, 'mp3')
    c.convert()
    oname = "%s/Output/flac/front.jpg" % (cwd,)
    tools.eq_(oname, c.destfilename)
    tools.ok_(os.path.exists(oname))

@tools.with_setup(_setup, _teardown)
def test_makedir():
    """Does makedir make the correct destination directory?"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'ogg')
    c.makedir()
    outdir = '%s/Output/flac' % (cwd,)
    tools.ok_(os.path.exists(outdir))

@tools.with_setup(_setup, _teardown)
@plugins.attrib.attr('slow')
def test_completeconversion():
    """Does the process work end to end?"""
    expected = {
        'title': [u'A test flac',],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    oname = '%s/Output/flac/%s.ogg' % (cwd, name)
    c = converter.Converter(fname, 'ogg')
    c.convert()
    tools.eq_(oname, c.destfilename)
    f = oggvorbis.Open(oname)
    for k, v in expected.items():
        tools.eq_(v, f[k])

@tools.with_setup(_setup, _teardown)
@tools.with_setup(make_single_output, delete_single_output)
def test_copyfile():
    """Test copying a file rather than converting it"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/flac/%s.flac' % (cwd, name)
    oname = '%s/Output/flac/%s.flac' % (cwd, name)
    c = converter.Converter(fname, 'flac')
    c.copyfile()
    tools.eq_(oname, c.destfilename)
    tools.ok_(os.path.exists(oname))
    
@tools.with_setup(_setup, _teardown)
def test_completecopy():
    """Does the copy process work end to end?"""
    expected = {
        'title': [u'A test mp3',],
        'artist': [u'Andy Theyers',],
        'album': [u'Portify Test Data',],
        'tracknumber': [u'01',],
        'date': [u'2010',],
        }
    cwd = os.path.dirname(os.path.realpath(__file__))
    name = '01 - artist - track title'
    fname = '%s/Input/mp3/%s.mp3' % (cwd, name)
    oname = '%s/Output/mp3/%s.mp3' % (cwd, name)
    c = converter.Converter(fname, 'mp3')
    c.convert()
    tools.ok_(os.path.exists(oname))
    f = easyid3.Open(oname)
    for k, v in expected.items():
        tools.eq_(v, f[k])

@tools.with_setup(_setup, _teardown)
def test_makedestfilename_supplemental():
    """Test that we're getting the right output file name for a file that is
    simply copied"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    fname = '%s/Input/flac/front.jpg' % (cwd,)
    c = converter.Converter(fname, 'mp3')
    tools.eq_(c.makedestfilename(), '%s/Output/flac/front.jpg' % (cwd,))
    
@tools.with_setup(_setup, _teardown)
def test_makedestfilename_convert():
    """Test that we're getting the right output file name for a file that is
    being converted"""
    cwd = os.path.dirname(os.path.realpath(__file__))
    fname = '%s/Input/flac/01 - artist - track title.flac' % (cwd,)
    c = converter.Converter(fname, 'mp3')
    tools.eq_(c.makedestfilename(), '%s/Output/flac/01 - artist - track title.mp3' % (cwd,))
    
    