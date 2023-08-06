============
html2docbook
============

This package contains transformation from HTML to DocBook XML.

Installation
============

- install **html2docbook** either using easy_install or by downloading the sources from the Python Cheeseshop


Supported platforms
===================

Unix


Subversion repository
=====================

- https://svn.zmag.de/svn/python/html2docbook


Usage
=====

Example from the Python command-line::

    >>> from html2docbook import Html2DocBook
    >>> h2d = Html2DocBook()
    >>> h2d.transform('<p>first paragraph</p><p>second paragraph</p>')
    '<section><para>first paragraph</para><para>second paragraph</para></section>'

License
=======

GPL


Author
======

Timo Stollenwerk | timo@zmag.de

