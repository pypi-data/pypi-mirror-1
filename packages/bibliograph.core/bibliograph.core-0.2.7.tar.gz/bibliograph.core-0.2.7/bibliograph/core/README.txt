bibliograph.core
================

Overview
--------

Core definitions of bibliograph packages

Here all bits and pieces are defined which are commonly used by the
packagages sharing the `bibliograph` namespace. We provide some interfaces
here:

IBibliographicReference is an interface for a single content object with a given
schema which can be rendered as a bibliographic entry (bibtex, endnote,
ris, etc.).

  >>> from bibliograph.core import interfaces
  >>> 'IBibliographicReference' in dir(interfaces)
  True

IBibliographyExport is a marker for a container directly
containing single exportable IBibliographicReference objects.

  >>> 'IBibliographyExport' in dir(interfaces)
  True

Another part of the package are utility methods and a collection of encodings
used within python and latex including a mapping.

A utility method `bin_search` is included. It acts like the `which`-command on
posix systems. It returns the full path of an executeable command, if it is
found in the PATH environment variable.

You may overload the PATH environment variable with another environment
variable: BIBUTILS_PATH. Executeables in this location will be found as well.

Resources
---------

- Homepage: http://pypi.python.org/pypi/bibliograph.core
- Code repository: http://svn.plone.org/svn/collective/bibliograph.core/

Contributors
------------

- Tom Gross, itconsense@gmail.com, Author
- Raphael Ritz, r.ritz@biologie.hu-berlin.de, Renderers
- Andreas Jung, info@zopyx.com, bugfixes
