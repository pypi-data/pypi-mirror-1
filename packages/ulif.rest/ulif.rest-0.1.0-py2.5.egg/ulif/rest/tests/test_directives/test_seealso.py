# $Id$
# Author: Uli Fouquet <uli@gnufix.de>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'seealso' directive.
"""

from __init__ import DocutilsTestSupport
import directives_plain
def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['seealso directive'] = [
["""\
.. seealso:: another_func
""",
"""\
<document source="test data">
    <admonition classes="seealso">
        <title>
            See also:
        <paragraph>
            another_func
"""],
["""\
.. seealso::

   The data is applied to this paragraph.

   And this one.
""",
"""\
<document source="test data">
    <admonition classes="seealso">
        <title>
            See also:
        <paragraph>
            The data is applied to this paragraph.
        <paragraph>
            And this one.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
