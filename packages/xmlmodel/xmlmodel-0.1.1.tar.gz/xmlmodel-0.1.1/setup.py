#!/usr/bin/env python
from distutils.core import setup

setup(
    name = 'xmlmodel',
    version = '0.1.1',
    description = 'Expressive XML Model Library',
    long_description = "XMLModel allows you to expressively define an " \
                       "XML document, using native python classes, " \
                       "you can then access the elements of the XML through " \
                       "a tree of native python objects.",
    author = 'Sean Jamieson',
    author_email = 'sean@barriescene.com',
    url = 'http://xmlmodel.acidreign.net',
    download_url = 'http://xmlmodel.acidreign.net/download',
    license = 'OSL3.0.',
    package_dir = {'xmlmodel' : ''},
    packages = ['xmlmodel'],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
