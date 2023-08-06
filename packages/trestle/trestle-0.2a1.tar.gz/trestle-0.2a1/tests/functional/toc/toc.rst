TOC placement test
------------------

.. fixtures :: toc
.. contents ::

One
===

No fails should show up in this category.

Two
===

A fail should be here, above the subhead.

.. request :: Before Two:Sub

   GET /fail
..

.. response ::

   fail!
..

Sub
^^^

No fails should be here.
