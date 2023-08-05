Overview
========

``zope.testbrowser`` provides an easy-to-use programmable web browser
with special focus on testing.  It is used in Zope, but it's not Zope
specific at all.  For instance, it can be used to test or otherwise
interact with any web site.

Changes
=======

3.4.1 (2007-09-01)
------------------

* Updated to mechanize 0.1.7b and ClientForm 0.2.7.  These are now
  pulled in via egg dependencies.

* ``zope.testbrowser`` now works on Python 2.5.

3.4.0 (2007-06-04)
------------------

* Added the ability to suppress raising exceptions on HTTP errors
  (``raiseHttpErrors`` attribute).

* Made the tests more resilient to HTTP header formatting changes with
  the REnormalizer.

3.4.0a1 (2007-04-22)
--------------------

Initial release as a separate project, corresponds to zope.testbrowser
from Zope 3.4.0a1
