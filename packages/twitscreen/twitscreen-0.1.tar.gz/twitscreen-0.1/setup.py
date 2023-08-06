#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2009, Thomas Jost <thomas.jost@gmail.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from distutils.core import setup

setup(
    name = "twitscreen",
    version = "0.1",
    scripts = ['twitscreen'],

    author = "Thomas Jost",
    author_email = "thomas.jost@gmail.com",
    description = "A simple screenshot utility that can crop images and upload them to Twitpic",
    license = "ISC",
    url = "http://github.com/Schnouki/twitscreen/tree/master",
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
    ],

    requires = [
        "pygtk",
        "pygtkimageview",
        "twitpic",
    ],
)
