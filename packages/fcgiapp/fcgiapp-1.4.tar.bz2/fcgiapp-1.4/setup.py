#!/usr/bin/env python
"""Distutils setup file"""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, Extension

setup(
    name="fcgiapp",
    version="1.4",
    description="C implementation of the FastCGI application protocol",

    long_description =
        "fcgiapp is a Python wrapper for the C FastCGI SDK.  It's used by "
        "PEAK's FastCGI servers to provide WSGI-over-FastCGI.  Originally "
        "created and maintained by Digital Creations (now Zope Corp.), it "
        "is now being maintained as one of PEAK's adopted \"orphan\" "
        "projects.  A POSIX-like operating system (Linux, Mac, Cygwin, etc.) "
        "is required, since Unix-domain socket use is hardwired in the "
        "original package.",

    author="Zope Corp. (formerly Digital Creations, LLC.)",
    author_email="n/a",
    
    #maintainer="Phillip J. Eby",
    #maintainer_email="peak@eby-sarna.com",

    license="MIT-style",
    platforms=['Posix','Cygwin'],
    ext_modules = [Extension("fcgiapp", ["fcgiappmodule.c", "fcgiapp.c"])],
    packages = [],
)

