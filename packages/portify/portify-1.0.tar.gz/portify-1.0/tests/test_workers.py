
"""Test worker registration"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

from nose import tools

from portify import workers

from workerdefn import flacbase
from workerdefn import mp3base
from workerdefn import oggbase

def setup():
    pass

def teardown():
    del workers.registry
    workers.registry = workers.Registry()
    
def test_basic():
    """Our first test.  Really ought to pass"""
    print "I am test"
    pass

def test_creation():
    """Create a worker - does it have the right attributes?"""
    flac = flacbase.copy()
    w = workers.Worker(**flac)
    tools.eq_(w.fmt, flac['fmt'])
    tools.eq_(w.mutagenklass, flac['mutagenklass'])
    tools.eq_(w.decode, flac['decode'])
    tools.eq_(w.encode, flac['encode'])
    tools.eq_(w.decodestdout, flac['decodestdout'])
    tools.eq_(w.encodestdin, flac['encodestdin'])
    flac.pop('fmt')
    tools.eq_(w.kwargs, flac)
    
def test_registration():
    """register a worker, can we get it back?"""
    flac = flacbase.copy()
    w = workers.Worker(**flac)
    r = workers.registry
    r.register(w)
    p = r.worker(flac['fmt'])
    tools.eq_(p, w)
    
@tools.raises(workers.NoWorkerRegistered)
def test_unregistration1():
    """Register a worker, unregister it, does it still exist?"""
    flac = flacbase.copy()
    w = workers.Worker(**flac)
    r = workers.registry
    r.register(w)
    r.unregister(flac['fmt'])
    r.worker(flac['fmt'])
    
@tools.raises(workers.NoWorkerRegistered)
def test_unregistration2():
    """Unregister a worker that wasn't registered"""
    r = workers.registry
    r.unregister('madeup')
    
def _register_all():
    """Register a full let of workers"""
    noencode = {
        'fmt': 'madeup',
        'mutagenklass': 'easyid3',
        'decode': 'lame -S --decode "%(input)s" "%(output)s"',
        'encode': None,
        'decodestdout': '-',
        'encodestdin': None,
        }
    r = workers.registry
    for defn in [flacbase, mp3base, oggbase, noencode]:
        w = workers.Worker(**defn)
        r.register(w)
        
def _unregister_all():
    """Unregister all of them"""
    r = workers.registry
    for fmt in ['flac', 'madeup', 'mp3', 'ogg']:
        r.unregister(fmt)
        
@tools.with_setup(_register_all, _unregister_all)
def test_outputtypes1():
    """Do we get the correct list of those available for encoding
    back?"""
    r = workers.registry
    tools.eq_(set(['flac', 'ogg', 'mp3']), set(r.outputtypes()))
    
@tools.with_setup(_register_all, _unregister_all)
def test_outputtypes2():
    """Is the madeup one not in outputtypes"""
    r = workers.registry
    tools.ok_('madeup' not in r.outputtypes())
    
@tools.with_setup(_register_all, _unregister_all)
def test_allworkers():
    r = workers.registry
    tools.eq_(len(r.allworkers()),4)
    
def test_exception():
    """Do we get the message we expect?"""
    r = workers.registry
    try:
        # Will raise an exception
        w = r.worker('madeup')
    except workers.NoWorkerRegistered, e:
        tools.eq_(str(e), 'No worker registered for madeup files')
    

        