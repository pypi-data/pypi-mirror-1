Trestle JSON support
--------------------

.. fixtures:: about_json

If simplejson_ is installed, Trestle uses a special output checker for output
that claims to be json data. When Trestle sees a response with the content
type "application/json", the json checker is automatically activated and used
in place of the normal output checker.

In the examples below, the full responses are:

.. request:: a list

   GET /list
..

.. response::

   [1, 2, 3, "a cow", "a monkey", [2, 5, 6], "the end"]
..

.. request:: a dict
   
   GET /dict
..

.. response::

   {"a": 1, "b": "hello", "another": [5, 1, 9], "sub": {"key": "value"}} 
..

.. request:: a string

   GET /string
..

.. response::

   "The quick brown dog jumped over the lazy fox. Again."
..

.. request:: a number

   GET /number
..

.. response::

   1293039483
..

When using the json output checker, a variety of wildcard-like
features are supported.

<any>
~~~~~

The special construct <any> may be used as a list term or dict key or
value. In a list, it matches one or more terms.

.. request:: a list

   GET /list
..

.. response::

   [1, 2, 3, "a cow", "a monkey", [2, 5, 6], "the end"]
..

.. response::
  
   [<any>]
..

.. response::

  [1, 2, 3, <any>]
..

.. response::
  
   [<any>, "the end"]
..

.. response::

   [<any>, "a cow", <any>]
..


In a dict, when used as a key **and value**, it matches one or more keys.

.. request:: a dict

   GET /dict
..

.. response::

   {"a": 1, "b": "hello", "another": [5, 1, 9], "sub": {"key": "value"}} 
..

.. response::

   {"a": 1, <any>: <any>}
..


<timestamp>
~~~~~~~~~~~

A timestamp wildcard matches strings of 6 or more contiguous digits.

.. request:: a timestamp-like number

   GET /number
..

.. response::

   <timestamp>
..


Source
^^^^^^

This document was built from the following .rst document:

.. include:: json.rst
   :literal:

Using this fixture module:

.. include:: about_json.py
   :literal:
   
.. _`simplejson` : http://pypi.python.org/pypi/simplejson
