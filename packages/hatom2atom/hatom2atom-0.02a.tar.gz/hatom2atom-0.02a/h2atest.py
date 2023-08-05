"""setup - test module to run html/atom test pairs in tests dir

Created and maintained by Luke Arno <luke.arno@gmail.com>

Copyright (C) 2006 Luke Arno <luke.arno@gmail.com> 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.

Luke Arno can be found at http://lukearno.com/
"""

from hatom2atom.util import easy_transform
from unittest import *
from glob import glob
from difflib import Differ
differ = Differ()

def make_test(name):
    """Return a func to test a html/atom pair."""
    def test_func():
        source = file('tests/%s.html' % name)
        expectation = file('tests/%s.atom' % name).read()
        result = easy_transform('xsl/hAtom2Atom.xsl', source)
        if expectation <> result:
            expection = expectation.splitlines(True)
            result = result.splitlines(True)
            raise AssertionError("".join(differ.compare(expectation, result)))
    test_func.__name__ = name
    test_func.__doc__ = "Generated test_func for test %s." % name
    return test_func

def gen_tests():
    """Generate a test function for each filename.atom in tests dir."""
    for name in (f[6:-5] for f in glob('tests/*.atom')):
        yield make_test(name)

def suite():
    """Create test suite for functions fro gen_tests"""
    return TestSuite((FunctionTestCase(fn) for fn in gen_tests()))
        
if __name__ == '__main__':
    TextTestRunner(suite()).run()

