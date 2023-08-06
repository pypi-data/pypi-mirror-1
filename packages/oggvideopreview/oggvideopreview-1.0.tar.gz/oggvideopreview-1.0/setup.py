#!/usr/bin/python
#
# python-oggvideopreview
#
# 2009 Fredrik Portstrom
#
# I, the copyright holder of this file, hereby release it into the
# public domain. This applies worldwide. In case this is not legally
# possible: I grant anyone the right to use this work for any
# purpose, without any conditions, unless such conditions are
# required by law.

from distutils.core import Extension, setup
setup(
    name = "oggvideopreview",
    version = "1.0",
    author = "Fredrik Portstrom",
    author_email = "fredrik@jemla.se",
    url = "http://fredrik.jemla.eu/oggvideopreview",
    description = "Get preview images from Theora videos in Ogg files",
    long_description = "python-oggvideopreview is a simple Python extension to "
    "get preview images from Theora videos in Ogg files. It uses libogg and "
    "libtheora.",
    license = "Public Domain",
    classifiers = [
        "License :: Public Domain",
        "Programming Language :: C"],
    ext_modules = [Extension(
            "oggvideopreview", ["oggvideopreview.c"],
            libraries = ["ogg", "theoradec"])])
