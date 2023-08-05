#!/usr/bin/env python
from distutils.core import Extension, setup

__revision__ = "$Id: setup.py 144 2006-07-12 16:52:51Z const $"

epoll = Extension(
    name = "epoll",
    sources = ["epoll.c"],
    )

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "License :: OSI Approved :: Python Software Foundation License",
    "Natural Language :: English",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: C",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

DESCRIPTION = """\
This python module provides access to epoll, I/O event
notification facility.
"""

setup(
    name = "pyepoll",
    version = "0.2",
    license = "PSF",
    description = "Python epoll wrapper",
    long_description = DESCRIPTION,
    author = "Constantin Baranov",
    author_email = "baranov86@mail.ru",
    url = "http://const.tltsu.ru/",
    download_url = "http://const.tltsu.ru/svn/const/pub/pyepoll/",
    platforms = ["linux2"],
    ext_modules = [epoll],
    classifiers = classifiers,
    )
