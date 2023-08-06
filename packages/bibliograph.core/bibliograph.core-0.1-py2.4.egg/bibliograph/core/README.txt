bibliograph.core Package Readme
===============================

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