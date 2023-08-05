##############################################################################
#
# Copyright (c) 2008 The Zope Foundation.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Additional roles for reference documentation.
"""

import re
from docutils import nodes, utils
from docutils.parsers.rst import roles

#import addnodes

# default is `literal`
innernodetypes = {
    'ref': nodes.emphasis,
    'term': nodes.emphasis,
    'token': nodes.strong,
}

ws_re = re.compile(r'\s+')
_litvar_re = re.compile('{([^}]+)}')

def deprecated_xfileref_role(typ, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    if text[0:1] == '!':
        text = text[1:]
        return [innernodetypes.get(typ, nodes.literal)(
            rawtext, text, classes=['xref'])], []
    pnode = addnodes.pending_xref(rawtext)
    pnode['reftype'] = typ
    # if the first character is a dot, search more specific namespaces first
    # else search builtins first
    if text[0:1] == '.' and \
       typ in ('data', 'exc', 'func', 'class', 'const', 'attr', 'meth'):
        text = text[1:]
        pnode['refspecific'] = True
    pnode['reftarget'] = ws_re.sub((typ == 'term' and ' ' or ''), text)
    pnode += innernodetypes.get(typ, nodes.literal)(rawtext, text,
                                                    classes=['xref'])
    return [pnode], []



def emph_literal_role(typ, rawtext, text, lineno, inliner, options={},
                      content=[]):
    text = utils.unescape(text)
    retnodes = []
    pos = 0
    for m in _litvar_re.finditer(text):
        if m.start() > pos:
            txt = text[pos:m.start()]
            retnodes.append(nodes.literal(txt, txt))
        retnodes.append(nodes.emphasis('', '', nodes.literal(m.group(1),
                                                             m.group(1))))
        pos = m.end()
    if pos < len(text):
        node = nodes.literal(text[pos:], text[pos:])
        node['classes'] += ['role', 'role-'+str(typ)]
        retnodes.append(node)
    return retnodes, []


specific_docroles = {
    'data': emph_literal_role,
    'exc': emph_literal_role,
    'func': emph_literal_role,
    'class': emph_literal_role,
    'const': emph_literal_role,
    'attr': emph_literal_role,
    'meth': emph_literal_role,

    'cfunc' : emph_literal_role,
    'cdata' : emph_literal_role,
    'ctype' : emph_literal_role,
    'cmacro' : emph_literal_role,

    'mod' : emph_literal_role,
    'keyword' : emph_literal_role,

    'ref': emph_literal_role,
    'token' : emph_literal_role,
    'term': emph_literal_role,

    'file' : emph_literal_role,
    'samp' : emph_literal_role,
}

for rolename, func in specific_docroles.iteritems():
    roles.register_canonical_role(rolename, func)
