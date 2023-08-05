#!/usr/bin/env python
from distutils.core import setup

setup(
    name="DeliciousAPI",
    version="1.0",
    description="Unofficial Python API for retrieving data from del.icio.us for research",
    long_description="""This module provides the following features:

    * getting a user's tags including tag counts, i.e. her tagging vocabulary
    * getting a url's so-called 'common tags', i.e. the most popular tags
      assigned to user bookmarks of said url, if any (number between 0 and 25)
    * getting the total number of bookmarks for a url, i.e. the number of
      users who have bookmarked the url
    * HTTP proxy support

    Note: Only public del.icio.us data will be mined (read below). This means
    that this API does not (yet) provide means to access your private bookmark
    data.

    The official del.icio.us API does not provide the functionality mentioned
    above, so this module will query the del.icio.us website directly and
    extract the required information by parsing the HTML code of the resulting
    web pages (a kind of poor man's web mining). The module is able to detect
    IP throttling, which is employed by del.icio.us to temporarily block
    abusive HTTP request behavior, and will raise a custom Python error to
    indicate that. Please be a nice netizen and do not stress the del.icio.us
    service more than necessary.

    It is strongly advised that you read the del.icio.us Terms of Use
    before using this Python module. In particular, read section 5
    'Intellectual Property'.

    The code is licensed to you under version 2 of the GNU General Public
    License.

    More information about this module can be found at
    http://www.michael-noll.com/2006/12/18/delicious-python-api/

    Copyright 2006-2007 Michael G. Noll <http://www.michael-noll.com/>
    """,
    author="Michael G. Noll",
    author_email="michael.g.noll@gmail.com",
    url="http://www.michael-noll.com/2006/12/18/delicious-python-api/",
    py_modules=['deliciousapi'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Sociology',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
