
"""Configuration - this will rapidly get superceded"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'
__version__ = '$Revision$'[11:-2]

import logging
import os
import sys

from ConfigParser import ConfigParser
from ConfigParser import NoOptionError
from ConfigParser import NoSectionError

from workers import Worker
from workers import registry

DEFAULTS = {
    'source': '~/Music',
    'destination': '~/mp3',
    'outputformat': 'mp3',
    'playable_formats': 'mp3',
    'loglevel': 'ERROR',
    'logfile': '/tmp/portify.log',
    'copyexts': 'jpg png jpeg jpe gif bmp',
    'encodestdin': 'false',
    'decodestdout': 'false',
    }

class ConfigError(Exception):
    pass

def start_logger(logfile, loglevel, verbose=False):

    logger = logging.getLogger('portify')
    loglevel = getattr(logging, loglevel)
    if verbose:
        hdlr = logging.StreamHandler(sys.stderr)
    else:
        hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(loglevel)
    logger.debug('logging system initialised')
    return logger


class Config(object):
    """In which we store our configuration"""
    
    def __init__(self, filename, **kwargs):
        config = ConfigParser(DEFAULTS)
        config.read(filename)
        loglevel = config.get('logging', 'loglevel')
        logfile = config.get('logging', 'logfile', vars=kwargs)
        verbose = kwargs.get('verbose', False)
        self.logger = start_logger(logfile, loglevel, verbose)
        self.source = os.path.expanduser(config.get('system', 'source'))
        self.destination = os.path.expanduser(config.get('system', 'destination'))
        self.outputformat = config.get('system', 'outputformat')
        self.playableformats = config.get('system', 'playableformats').split(" ")
        self.copyexts = config.get('system', 'copyexts').split(" ")
        if self.outputformat not in self.playableformats:
            self.playableformats.append(self.outputformat)
        self.registerworkers(config)
        
    def registerworkers(self, config):
        """Register the workers - they are of the format:
        [mp3]
        mutagenklass = easyid3
        decode = lame -S --decode "%(input)s" "%(output)s"
        encode = lame -h -V 2 --vbr-new "%(input)s" "%(output)s"
        decodestdout = -
        encodestdin = -
        
        [flac]
        mutagenklass = flac
        decode = flac -sd -o "%(output)s" "%(input)s"
        encode = flac -s "%(input)s" "%(output)s"
        decodestdout = -
        encodestdout = -
        
        [ogg]
        mutagenklass = oggvorbis
        decode = oggdec -o "%(output)s" "%(input)s"
        encode = oggenc "%(input)s" -Q -q 4 -o "%(output)s"
        decodestdout = -
        encodestdout = -
        
        [madeupformat]
        mutagenklass = None
        decode = None
        encode = None
        decodestdout = None
        encodestdout = None
        """
        for section in config.sections():
            if section in ['logging', 'system']:
                # we are not a worker
                continue
            worker = self._makeworker(section, config)
            registry.register(worker)
            
    def _makeworker(self, section, config):
        d = dict(config.items(section, raw=True))
        return Worker(section, **d)
    
    