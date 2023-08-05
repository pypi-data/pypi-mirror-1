# $Id$
# Author: Uli Fouquet <uli@gnufix.de>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'data' directive.
"""

from __init__ import DocutilsTestSupport
import directives_plain
def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['data directive'] = [
["""\
.. data:: foo bar
""",
"""\
<document source="test data">
    <admonition classes="desc-data" desctype="data">
        <inline first="False">
            <inline>
                foo bar
        <container>
"""],
["""\
.. data:: foo bar

   The data is applied to this paragraph.

   And this one.
""",
"""\
<document source="test data">
    <admonition classes="desc-data" desctype="data">
        <inline first="False">
            <inline>
                foo bar
        <container>
            <paragraph>
                The data is applied to this paragraph.
            <paragraph>
                And this one.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
