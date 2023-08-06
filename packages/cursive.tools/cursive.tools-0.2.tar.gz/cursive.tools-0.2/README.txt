
``cursive.tools``: Tools for authoring restructured text files
==============================================================

This package provides a ``cursive`` command that is intended to become
the core of a whole set of tools for working with `reStructured Text`_
documents.  The command supports sub-commands, some of which come
built-in with this package, and others that become available as other
cursive modules are installed.

The single built-in command available at this point is:

``cursive wc <filename>``
    Word count: ignoring headers, code snippets, and comments, this
    routine figures out the number of words in your document, and prints
    out a total both for each section of your document separately and
    also for the document as a whole.

The other module currently available to supplement cursive is the
`cursive.pymag`_ package, which will format an article for publication
in Python Magazine.

.. _reStructured Text: http://docutils.sourceforge.net/rst.html
.. _cursive.pymag: http://pypi.python.org/pypi/cursive.pymag/
