
"""Classes to walk the filesystem and check whether a given file should be
converted, copied or left"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import logging
import os

import config
import workers

class Checker(object):
    """Check if the given file should be converted"""
    
    def __init__(self, inputfile, outputfile):
        self.inputfile = inputfile
        self.outputfile = outputfile
        basename, self.sourcefmt = os.path.splitext(self.inputfile)
        self.filetype = self.sourcefmt[1:]
        
    def alreadythere(self):
        """For the configured output format and path, is there already a file
        there?"""
        if os.path.exists(self.outputfile):
            return True
        return False
        
    def morerecent(self):
        """If there is already a file there, is it more recent than the input
        file?"""
        if os.stat(self.inputfile).st_mtime > os.stat(self.outputfile).st_mtime:
            return True
        return False
        
    def shouldconvert(self):
        if self.filetype not in workers.registry.outputtypes():
            # Can't convert this type of file
            if self.filetype not in config.config.copyexts:
                # And it's not file we should copy across
                return False
        if self.alreadythere():
            # Is there already an output file of the right format?
            if self.morerecent():
                # If the input file is more recent, we want to convert again
                return True
            return False
        return True

    __call__ = shouldconvert
    
class Walker(object):
    """Walk the file system, looking for files. Maintain a list of all files
    to convert"""
    
    def __init__(self, 
                  inputroot=None, 
                  outputroot=None, 
                  outputformat=None):
        # Note the weird construct here - it is because config.config is
        # evaluated at run time, not whenever this module is imported.
        c = config.config
        self.inputroot = inputroot if inputroot else c.source
        self.outputroot = outputroot if outputroot else c.destination
        self.outputformat = outputformat if outputformat else c.outputformat
        logger = logging.getLogger("portify")
        logger.info("Walker initiated with source %s and destination %s" % (self.inputroot, self.outputroot))
        
    def makeoutputfilename(self, filename):
        c = config.config
        basename, ext = os.path.splitext(filename)
        ext = ext[1:]
        if ext in c.copyexts + c.playableformats:
            path, fname = os.path.split(filename)
            newfile = "%s%s/%s" % (self.outputroot, path[len(self.inputroot):], fname)
        else:
            d = "%s.%s" % (basename, self.outputformat)
            newfile = "%s%s" % (self.outputroot, d[len(self.inputroot):])
        return newfile
    
    def walk(self):
        for item in os.walk(self.inputroot):
            if item[2]:
                for f in item[2]:
                    filename = "%s/%s" % (item[0], f)
                    if Checker(filename, self.makeoutputfilename(filename))():
                        yield filename