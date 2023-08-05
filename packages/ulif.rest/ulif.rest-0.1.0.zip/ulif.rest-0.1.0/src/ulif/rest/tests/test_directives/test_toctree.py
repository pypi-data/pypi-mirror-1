# $Id$
# Author: Uli Fouquet <uli@gnufix.de>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'toctree' directive.
"""

from __init__ import DocutilsTestSupport
import directives_plain
def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['toctree directive'] = [
["""\
.. toctree::

   file1.rst
   file2.rest
   foo
""",
"""\
<document source="test data">
    <comment includefiles="file1.rst file2.rest foo" maxdepth="-1" xml:space="preserve">
"""],
["""\
.. toctree::
   :maxdepth: 2

   file1.rst
   file2.rest
   foo
""",
"""\
<document source="test data">
    <comment includefiles="file1.rst file2.rest foo" maxdepth="2" xml:space="preserve">
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
