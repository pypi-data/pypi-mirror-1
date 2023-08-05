# $Id$
# Author: Uli Fouquet <uli@gnufix.de>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'function' directive.
"""

from __init__ import DocutilsTestSupport
import directives_plain
def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['function directive'] = [
["""\
.. function:: myfunction(param1[, param2=None])
""",
"""\
<document source="test data">
    <admonition classes="desc-function" desctype="function">
        <inline first="False">
            <strong>
                myfunction
            <inline>
            <inline>
                (
                <emphasis>
                    param1
                <inline>
                    [
                    <inline>
                        , \n\
                    <emphasis>
                        param2=None
                    <inline>
                        ]
            <inline>
                )
        <container>
"""],
["""\
.. function:: myfunction()

   The function is applied to this paragraph.

   And this one.
""",
"""\
<document source="test data">
    <admonition classes="desc-function" desctype="function">
        <inline first="False">
            <strong>
                myfunction
            <inline>
                ()
        <container>
            <paragraph>
                The function is applied to this paragraph.
            <paragraph>
                And this one.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
