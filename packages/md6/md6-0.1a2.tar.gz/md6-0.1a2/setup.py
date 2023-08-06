# MD6 Python wrapper
# Copyright (c) 2009 Christian Heimes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
import os
import sys
import struct
from glob import glob

from Cython.Distutils import build_ext
from distutils.extension import Extension
from distutils.core import setup

is64bit = struct.calcsize("P") == 8

md6_src = ("md6_compress.c", "md6_mode.c", "md6_nist.c")
if is64bit:
    md6_base = "opt64"
else:
    md6_base = "opt32"

sources = ["md6/pymd6.pyx"] 
for src in md6_src:
    sources.append(os.path.join(md6_base, src))

md6ext = Extension("md6._md6",
    sources,
    depends=["setup.py"] + glob(os.path.join(md6_base, "*.h")),
    include_dirs = [md6_base]
    )

setup(
    name = "md6",
    version = "0.1a2",
    description = "MD6 wrapper for Python",
    cmdclass = {'build_ext': build_ext},
    ext_modules = [md6ext],
    packages = ["md6"],
    author = "Christian Heimes",
    author_email = "christian@cheimes.de",
    license = "MIT",
    keywords = "md6 hash",
    classifiers = (
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: Security :: Cryptography',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ),
)
