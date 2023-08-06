Trestle XML Support
-------------------

.. fixtures:: about_xml

If lxml_ is installed, Trestle uses a special output checker for output that
claims to be xml or html, using the output checker from the
lxml.doctestcompare module by Ian Bicking. 

The example matching and diff output rules are covered in the documentation
for that module. Here's a summary, quoted from that documentation:

"When trestle sees a response with an xml or html content type, it compares the
expected response with the actual response as xml or html documents. Some
rough wildcard-like things are allowed.  Whitespace is generally ignored
(except in attributes).  In text (attributes and text in the body) you can use
``...`` as a wildcard.  In an example it also matches any trailing tags in the
element, though it does not match leading tags.  You may create a tag
``<any>`` or include an ``any`` attribute in the tag.  An ``any`` tag matches
any tag, while the attribute matches any and all attributes.

"When a match fails, the reformatted example and gotten text is
displayed (indented), and a rough diff-like output is given.  Anything
marked with ``-`` is in the output but wasn't supposed to be, and
similarly ``+`` means it's in the example but wasn't in the output."[1]_

Examples
^^^^^^^^

.. request:: Get some xml

  GET /
..

.. response::

  <hello>
    This is some xml <a val="1" />.
  </hello>
..

.. request:: Get some html

   GET /html
..

.. response::
   <html>
        <p>Even fairly broken html is supported
   </html>
..


Source
^^^^^^

This document was built from the following .rst document:

.. include:: xml.rst
   :literal:

Using this fixture module:

.. include:: about_xml.py
   :literal:
   
.. _lxml : http://codespeak.net/lxml/

.. [1] From the docstring of lxml.doctestcompare. lxml is copyright Infrae
   and distributed under the BSD license (see BSD.txt)        
