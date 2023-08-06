
"""Setup"""

__author__ = 'Andy Theyers <andy.theyers@isotoma.com>'
__docformat__ = 'restructuredtext en'

import os

from setuptools import find_packages
from setuptools import setup

execfile(os.path.join(os.path.dirname(__file__), "portify", "release.py"))

long_description = """Point it at the root of your music library and it
will create a  mirror of the library in your chosen portable format, 
directory structure and all.  Tags are maintained, as is your file
naming convention."""

setup(
    name="portify",
    packages=find_packages(),
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    download_url=download_url,
    install_requires=[
        'mutagen',
        'nose',
        ],
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
