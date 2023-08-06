============================
collective.transform.docbook
============================

This package contains a portal transformation that is capable converting HTML into DocBook.

Basic usage
-----------

The basic usage is turning HTML into DocBook:

    >>> from collective.transform.docbook.html_to_docbook import Html2DocBook
    >>> text = '<p>first paragraph</p><p>second paragraph</p>'
    >>> h2d = Html2DocBook()
    >>> h2d.convert(text)
    '<section><para>first paragraph</para><para>second paragraph</para></section>'
