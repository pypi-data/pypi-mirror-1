# $Id$
# Author: Uli Fouquet <uli@gnufix.de>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'version' directive.

Includes test for ``deprecated``, ``versionadded`` and
``versionchanged``.
"""

from __init__ import DocutilsTestSupport
import directives_plain
def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

# 
totest['version directives'] = [
    # version directives must have an argument...
["""\
.. deprecated::
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Error in "deprecated" directive:
            1 argument(s) required, 0 supplied.
        <literal_block xml:space="preserve">
            .. deprecated::
"""],
    # version directives must have content...
["""\
.. deprecated:: foo
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            The "deprecated" admonition is empty; content required.
        <literal_block xml:space="preserve">
            .. deprecated:: foo
"""],
["""\
.. deprecated:: 1.0a

   The data is applied to this paragraph.

   And this one.
""",
"""\
<document source="test data">
    <admonition classes="deprecated">
        <title>
            Deprecated from version 1.0a: \n\
        <paragraph>
            The data is applied to this paragraph.
        <paragraph>
            And this one.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
