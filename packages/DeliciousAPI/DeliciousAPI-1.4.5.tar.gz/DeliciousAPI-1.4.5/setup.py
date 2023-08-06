#!/usr/bin/env python
from distutils.core import setup

setup(
    name="DeliciousAPI",
    version="1.4.5",
    keywords='del.icio.us delicious api research social bookmarking python',
    description="Unofficial Python API for retrieving data from del.icio.us",
    long_description="""This module provides the following features plus some more:

    * getting a url's full history with
        * users who bookmarked the url including tags used for such bookmarks
          and the creation time of the bookmark in YYYY-MM format
        * common tags (up to a maximum of 25) including weight (0...5)
    * getting a user's full bookmark collection including private bookmarks
      IF you know username AND password
    * getting a user's most recent public bookmarks (up to 100; via RSS feed)
    * getting a user's full public tagging vocabulary, i.e. tags and tag counts
    * HTTP proxy support

    The official del.icio.us API does not provide all the functionality mentioned
    above, and in such cases this module will query the del.icio.us *website*
    directly and extract the required information by parsing the HTML code of the
    resulting web pages (a kind of poor man's web mining). The module is able to
    detect IP throttling, which is employed by del.icio.us to temporarily block
    abusive HTTP request behavior, and will raise a custom Python error to
    indicate that. Please be a nice netizen and do not stress the del.icio.us
    service more than necessary.

    It is strongly advised that you read the del.icio.us Terms of Use
    before using this Python module. In particular, read section 5
    'Intellectual Property'.

    The code is licensed to you under version 2 of the GNU General Public
    License.

    More information about this module can be found at
    http://www.michael-noll.com/wiki/Del.icio.us_Python_API

    Copyright 2006-2008 Michael G. Noll <http://www.michael-noll.com/>

    """,
    author="Michael G. Noll",
    author_email="coding[AT]michael-noll[DOT]com",
    license='GNU General Public License version 2',
    url="http://www.michael-noll.com/wiki/Del.icio.us_Python_API",
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
    install_requires=["FeedParser>=0.4.1", "BeautifulSoup>=3.0.7"],
)
