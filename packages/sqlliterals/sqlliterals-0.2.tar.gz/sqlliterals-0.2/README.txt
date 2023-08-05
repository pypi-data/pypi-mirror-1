Introduction
------------

The sqlliterals distribution consists of a package containing two different
implementations of SQL statement tokenisation for the detection of literal
regions in such statements. It also provides a function which can replace
one kind of parameter marker with another in statements, subject to the
careful choice of the original parameter marker (since the replacement process
builds on the above tokenisation process and the identification of non-literal
regions).

Examples
--------

See the test.py file for some tests and simple examples which use the parsing/
tokenising and replacement functions.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for sqlliterals at the time of release is:

http://www.python.org/pypi/sqlliterals

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

The sqlliterals.pyparser package has the following dependency:

Package                     Release Information
-------                     -------------------

pyparsing                   Tested with 1.2

New in sqlliterals 0.2 (Changes since sqlliterals 0.1)
------------------------------------------------------

  * Added a replace function to the different modules which permits the
    replacement of carefully chosen parameter markers with markers having a
    different representation.

Release Procedures
------------------

Update the sqlliterals/__init__.py __version__ attribute.
Update the release notes (see above).
Check the release information in the PKG-INFO file.
Tag, export.
Archive, upload.
Update PyPI entry.
