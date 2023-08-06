
"""Worker definitions"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

mp3base = {'fmt': 'mp3',
           'mutagenklass': 'easyid3',
           'decode': 'lame -S --decode "%(input)s" "%(output)s"',
           'encode': 'lame -S -h -V 2 --vbr-new --tt "" --ta "" --tl "" --tn "" --ty "" --tg "" "%(input)s" "%(output)s"',
           'decodestdout': '-',
           'encodestdin': '-',
           }

flacbase = {'fmt': 'flac',
            'mutagenklass': 'flac',
            'decode': 'flac -sd -o "%(output)s" "%(input)s"',
            'encode': 'flac -s "%(input)s" "%(output)s"',
            'decodestdout': '-',
            'encodestdin': '-',
            }

oggbase = {'fmt': 'ogg',
           'mutagenklass': 'oggvorbis',
           'decode': 'oggdec -Q -o "%(output)s" "%(input)s"',
           'encode': 'oggenc "%(input)s" -Q -q 4 -o "%(output)s"',
           'decodestdout': '-',
           'encodestdin': '-',
           }

