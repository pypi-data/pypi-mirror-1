
RestructuredText (ReST) Extensions
==================================

What is this?
-------------

The extensions collected in this package provide support for some of
the markup used in RestructuredText documents of the stock Python
documentation toolchain.

RestructuredText is a document markup language with special human
readable markup, that is widely spread in the Python
world. RestructuredText documents are a bit like HTML but better
readable. The text you are reading, for example, is written as ReST.

See::

	http://docutils.sourceforge.net/rst.html

to learn more about ReST (and ``docutils``).

Normally, ReST documents can be processed with tools of the Python
package ``docutils``. The ``docutils`` include so-called readers,
parsers, writers and publishers for reading ReST documents and writing
various output formats like HTML, XML or LaTeX.

Since Python switched from LaTeX to ReST documentation with the 2.6
version, some special markup was introduced like ``function``,
``seealso`` or ``versionchanged``, that helps to describe a
programming API more precisely. These additional 'tags', however,
needed specialized readers, parsers, writers and publishers to be
understood. The normal docutils tools did not understand the new roles
and directives.

This package makes it possible to use the standard ``docutils``
parsers and writers with the additional roles and directives listed
below.


Prerequisites and requirements
------------------------------

- ``docutils`` -- version 0.4 is recommended. 

  It can be retrieved from http://docutils.sourceforge.net/.

- ``Pygments`` -- a syntax highlighter.

  It can be retrieved from http://pygments.org/. This is only needed,
  if you want syntax highlighting of code fragments in your ReST
  documents.

  Because there is currently only support for HTML with pygments, you
  won't use it for other output formats. In this case you don't need
  pygments. 

Both packages can also retrieved via cheeseshop and ``easy_install``.


Activate support for the additional set of roles/directives
-----------------------------------------------------------

Just import the modules in this package::

  from ulif.rest import directives_plain
  from ulif.rest import roles_plain
  from ulif.rest import pygments_directive # for syntax-highlighting support

That's it. The modules define and register the new roles and
directives with the ``docutils`` automatically. You don't have to call
a special function.


Running the tests
-----------------

Call ``tests/alltests.py`` with your favourite Python interpreter::

  $ python tests/alltests.py

Note, that ``docutils`` must be available in your PYTHON_PATH.

If you installed the source version with buildout (not an egg), you
can generate a ``buildout`` executable in the bin/ directory of the
source root and run::

  $ bin/test


Which roles and directives are supported:
-----------------------------------------

``pygments_directive`` adds the following new directives:

- `sourcecode` -- a directive to highlight syntax of the following
                  code block. It takes one parameter, the language,
                  and currently only supports HTML output.

                  Example::

                    .. sourcecode:: python

                       class Cave(object):
                            pass

                    This will render the class definition with
                    colours.

		    An additional optional parameter is ``linenos``,
		    which adds linenumbers to the code::

		    .. sourcecode:: python
                       :linenos:

                       class NumberedCave(object):
                           pass

	            will render the code block with line numbering.

                    See the source for further options.
		    

- `code-block` -- an alias for `sourcecode`.


``directives_plain`` adds the follwing new directives:

- `function` -- a directive to describe functions with their
                signature.

- `data` -- ???

- `class` -- a directive to define a Python class.

- `method` -- a directive to describe the method of a Python class.

- `attribute` -- a directive to describe an attribute of a Python
                 class.

- `exception` -- a directive to describe an exception.

- `cmdoption` -- a directive to describe a command option.

- `envvar` -- a directive to describe an environment variable.

- `describe` -- a directive to describe something.


- `seealso` -- a directive to add a 'See also' subsection. It requires
               some 'body'-text.

- `deprecated` -- a directive to add a deprecation warning. It also
                  requires some explanatory body text and a version
                  number.

- `versionadded` -- a directive to add a note that tells, in which
                    version the surrounding thing was added to the
                    API.
          
                    Requires a version number and an explanatory text.

                    Example::

                      .. versionadded:: 0.11

                         Added for convenience reasons.

- `versionchanged` -- a directive to add a note that tell, in which
                      version a signature or something else changed
                      and why.

                      Example::

                        .. versionchanged:: 0.11

                          Added cave parameter, because every caveman
                          needs a cave.

- `toctree` -- a directive that requests to generate a
               table-of-contents tree of files, given in the body part
               of the directive. The so-called toc-tree will not
               be generated by standard writers, because it needs at
               least two parsing passes (one to collect all
               references, another pass to generate the reference
               targets).

	       If you insert a toctree directive in a document, this
	       will not block parsing of the document any more, but 
	       the toctree will be 'invisible' in rendered documents.

	       The toctree directive supports a ``maxdepth``
	       parameter, a number, that tells, to which depth a
	       toctree should be generated (default: no limit).

	       Example::

                 .. toctree::
                    :maxdepth: 2

                    chapter1.rst
                    chapter2.rst
                    another_file.rst

	         This should render a table of contents with the
	         headings of the three given files. Only headers of
	         level 1 and 2 will be included in the toctree.

``roles_plain`` adds the following new roles:

- `data`

- `exc`

- `func`

- `class`

- `const`

- `attr`

- `meth`

- `cfunc`

- `cdata`

- `ctype`

- `cmacro`

- `mod`

- `keyword`

- `ref`

- `token`

- `term`

- `file`

- `samp`

Every role can be used like this :<rolename>:`<text>`. For example
:func:`my_function` will output the text ``my_function``, rendered in
a different way than normal text. The exact kind of rendering depends
on the writer and translator that is used. In usual HTML writers it
will be rendered with roman fonts.

The same applies to all the other roles.

