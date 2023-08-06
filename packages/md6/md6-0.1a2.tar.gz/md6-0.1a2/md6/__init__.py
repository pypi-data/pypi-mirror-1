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
from md6._md6 import MD6

def md6(data=None):
    """MD6 (256)
    """
    m = MD6(256)
    if data is not None:
        m.update(data)
    return m

md6_256 = md6

def md6_224(data=None):
    """MD6 (224)
    """
    m = MD6(224)
    if data is not None:
        m.update(data)
    return m

def md6_384(data=None):
    """MD6 (384)
    """
    m = MD6(384)
    if data is not None:
        m.update(data)
    return m

def md6_512(data=None):
    """MD6 (512)
    """
    m = MD6(512)
    if data is not None:
        m.update(data)
    return m
