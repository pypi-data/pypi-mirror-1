
"""The Converter classes"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

try:
    import hashlib as hasher
except ImportError:
    import md5 as hasher

import datetime
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time

import config
import filesystem
from workers import registry

def unique_file():
    d = datetime.datetime.now()
    assert isinstance(d, datetime.datetime)
    ds = time.strftime("%A, %d %B %Y %H:%M:%S +0000", d.timetuple()) + " %.7f" % (time.time(),)
    filename = "%s/%s.wav" % (tempfile.gettempdir(), hasher.md5(ds).hexdigest(),)
    return filename

class Converter(object):
    
    """Our base convertor"""
    
    core_tags = [
        'artist',
        'title',
        'album',
        'date',
        'tracknumber',
        'genre',
        ]
    
    def __init__(self, sourcefile, fmt=None):
        self.sourcefile = sourcefile
        self.destfmt = fmt if fmt else config.config.outputformat
        basename, self.sourcefmt = os.path.splitext(self.sourcefile)
        self.destfilename = self.makedestfilename()
        self.sourcefmt = self.sourcefmt[1:]
        self.logger = logging.getLogger("portify")
        if self.sourcefmt not in config.config.copyexts:
            self.sourceworker = registry.worker(self.sourcefmt)
            self.destworker = registry.worker(self.destfmt)
        
    def makedestfilename(self):
        """Make the right destination file name"""
        # if source extension is either copyable, or in playable formats
        # we want to copy it, otherwise we want to make to make one with
        # the converted 
        c = config.config
        basename, ext = os.path.splitext(self.sourcefile)
        ext = ext[1:]
        if ext in c.copyexts + c.playableformats:
            path, fname = os.path.split(self.sourcefile)
            newfile = "%s%s/%s" % (c.destination, path[len(c.source):], fname)
            return newfile
        else:
            basename, sourcefmt = os.path.splitext(self.sourcefile)
            d = "%s.%s" % (basename, self.destfmt)
            dest = "%s%s" % (c.destination, d[len(c.source):])
            return dest
            
    def convert(self):
        """Do the actual work"""
        self.makedir()
        c = config.config
        fname, ext = os.path.splitext(self.sourcefile)
        ext = ext[1:]
        if ext in c.copyexts + c.playableformats:
            self.copyfile()
            c.logger.info("Copied %s to %s" % (self.sourcefile, self.destfilename))
        else:
            self.convertaudio()
            c.logger.info("Converted %s to %s" % (self.sourcefile, self.destfilename))
            self.movetags()
        
    __call__ = convert
    
    def makedir(self):
        """Make the destination directory, if it doesn't exist"""
        dirname = os.path.dirname(self.destfilename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            
    def copyfile(self):
        """Copy the file rather than convert it"""
        shutil.copy(self.sourcefile, self.destfilename)
        
    def movetags(self):
        """Move the tags"""
        t = self.gettags()
        self.writetags(t)
        
    def gettags(self):
        """In which we get the tags from the source file"""
        # use worker.mutagenklass
        klass = 'mutagen.%s' % (self.sourceworker.mutagenklass,)
        __import__(klass)
        m = sys.modules[klass]
        return m.Open(self.sourcefile)
    
    def writetags(self, tags):
        """In which we write tags to the destination file"""
        if not os.path.exists(self.destfilename):
            raise IOError("Destination file %s not found" % (self.destfilename,))
        klass = self.destworker.mutagenklass
        __import__("mutagen.%s" % (klass,))
        m = sys.modules["mutagen.%s" % (klass,)]
        outfile = m.Open(self.destfilename)
        if hasattr(outfile, 'valid_keys'):
            # special case for those file formats with limited tags
            for k in outfile.valid_keys.keys():
                if tags.get(k, None) is not None:
                    outfile[k] = tags[k]
        else:
            # more generic case for sensible file formats
            outfile.update(tags)
        outfile.save()
        
    def convertaudio(self):
        """In which we convert the audio"""
        if self.sourceworker.decodestdout == '-' and self.destworker.encodestdin == '-':
            self._streamedconvert()
        else:
            self._filebasedconvert()
            
    def _make_cmd(self, cmd, params):
        """Make a suitable list to be passed to subprocess.Popen"""
        l = cmd.split()
        l[l.index('"%(input)s"')] = params['input']
        l[l.index('"%(output)s"')] = params['output']
        return l
    
    def _streamedconvert(self):
        """Both our workers can decode to or encode from stdout/in"""
        decode = self._make_cmd(self.sourceworker.decode,
                                {'input': self.sourcefile, 'output': '-'})
        encode = self._make_cmd(self.destworker.encode,
                                {'output': self.destfilename, 'input': '-'})
        p1 = subprocess.Popen(decode, stdout=subprocess.PIPE)
        p2 = subprocess.Popen(encode, stdin=p1.stdout, stdout=subprocess.PIPE)
        p2.wait()
        
    def _filebasedconvert(self):
        """One or other of our workers cannot take stdout/in, so we create a temporary file
        instead"""
        tmpfile = unique_file()
        decode = self._make_cmd(self.sourceworker.decode,
                                {'input': self.sourcefile, 'output': tmpfile})
        encode = self._make_cmd(self.destworker.encode,
                                {'output': self.destfilename, 'input': tmpfile})
        subprocess.call(decode)
        subprocess.call(encode)
        os.unlink(tmpfile)
    
class Runner(object):
    
    def __init__(self, configobject):
        config.config = configobject
        self.walker = filesystem.Walker()
        
    def run(self):
        for fname in self.walker.walk():
            con = Converter(fname)
            con.convert()
            
    __call__ = run
    
