Trestle: doctest for REST(ful services)
---------------------------------------

.. fixtures:: about
.. contents::

About
~~~~~

Trestle is a nose plugin that enables you to write testable documentation for
web apps (or shell commands, but more on that later).

To use trestle, write a `reStructured Text`_ document (like this one) using a
set of special directives to indicate the **fixtures** to be used for testing
(including the http or mock http client), each **request** to be sent via the
client, and the **expected response** from the application under test.

A simple trestle test document might look like this::

  Frog: A web service for doing things with frogs
  -----------------------------------------------

  .. fixtures :: frog_fixtures

  Frog is a web service for doing things with frogs.
  
  You can list the available frogs. 
  
  .. request :: List available frogs

     GET /frogs
  ..

  The response is in a plain-text format.
  
  .. response ::
    
     bullfrog
     poison dart
     treefrog
     ...
  ..

  You can find out if something is a frog.

  .. request :: Get bullfrog details

     GET /frogs/bullfrog
  ..

  If the requested term is a frog, details about the frog will be returned.
  
  .. response ::

     Bullfrogs are really big frogs.
  ..

  Otherwise, a 404 response is returned.

  .. request :: Get details for a non-frog

     GET /frogs/toad
  ..

  .. response ::

     404 ...
     ...
     
     "toad" is not a frog.
  ..

  You can create frogs.

  .. request :: Create a frog

     POST /frogs/pouched+frog
     A pouched frog camouflages itself to look like dead leaves.
  ..

  .. response ::

     201 Created
     ...

     ...
  ..

Trestle directives
^^^^^^^^^^^^^^^^^^
  
Fixtures for a trestle test file are set like so::

  .. fixtures:: about

A fixtures directive is required in every document to be tested. The
directive must name a python module. The module must include the
following attribute:
  
client
  A client application to be called with methods .get(), .post(),
  .put(), etc. Each method must accept at least the arguments url and
  data, and may accept others but may not require
  them. `paste.fixtures.TestApp`_ is such a client, though it natively
  supports only .get() and .post().

And may include the following functions:

setup_all(cls)
  Setup fixture run before the first request.

teardown_all(cls)
  Teardown fixture run after the last request.

setup_each(inst)
  Setup fixture run before each request.

teardown_each(inst)
  Teardown fixture run after each request.

Tests in a trestle document consist of a ``.. request`` directive, followed by
one or more ``.. response`` directives. The ``.. request`` directive defines
the request to be sent to the web app under test, using the client defined in
the fixtures module.
  
A simple request directive looks like this::

  .. request:: A simple get

    GET /foo/bar
  ..

If the request is a POST or PUT that includes data to be sent, include
that data in the body of the request, after the request line::

  .. request:: A post

    POST /foo/bar
    a=1&b=2
  ..

The response expected to be returned to the client is defined using a
response block::

  .. response::

    Ponies!!1!
  ..


.. note:: Conclude each block with ``..`` alone on a line to avoid rst parsing
          errors that can result in text following a block being thrown away.

The testing process is simple: each request is executed using the
client defined in the fixtures module, and each expected response
following that request in the text is compared against the actual
response. If all responses match, the test passes. Otherwise, it
fails.

.. raw:: html

  <p>Passing examples are given a <span class="pass">pleasing green 
     background</span>, failures a <span class="fail">sinister red</span>. 
     Details of the failed match are included following the
     failed example.</p>


Fixture commands
^^^^^^^^^^^^^^^^

At times it may be necessary to execute a unique fixture before executing a
request. While it's usually better to make the test depend only on public apis
and not internal details or externalities, sometimes (e.g. when testing
time-dependent operations) that isn't possible or reasonable. For those times,
use the **:setup:** argument to the request. The body of the exec argument
will be evaluated in the context of the fixture module before running the
request. Naturally, there is also a **:teardown:** argument, which will be
executed after the request is run and the response processed. Here's an
example::

  .. request:: Get something special
     :setup: client.set_special(true)
     :teardown: client.set_special(false)

     GET /special
  ..

  
Shell examples
^^^^^^^^^^^^^^
  
Trestle also supports shell examples. When a shell example is executed, the
shell command given is executed, and the stdout produced by the command is
compared to the body of the ``..shell`` example using the normal doctest
output checker. A simple shell example looks like this::

 .. shell :: echo "Hello"

    Hello
 ..

Shell examples support the standard ``:setup:`` and ``:teardown`` options, as
well as three others: ``:cwd:``, which can be used to set the cwd of the shell
command; ``:post:``, which names a fixture callable to be used to post-process
the output of the shell command before checking it against the expected
output, and the flag ``:stderr:``, which indicates that the example output
should be compared against the stderr output of the shell command, rather than
stdout (which is the default).
 
Examples
~~~~~~~~

The application used by this self test is very simple: it always replies with
'Hello' to GET requests, unless **special** mode is active. Let's start the
test examples with a simple GET request.

.. request:: A simple get

   GET /foo
.. 

You can match on the whole response -- be sure to always include both
the full status line and headers:

.. response::
 
   200 Ok
   Content-type: text/plain

   Hello
..

Or just the content. Notice that multiple response blocks can be
compared against the same request.

.. response::

   Hello
..

The output comparison is done using a doctest OutputChecker. The
doctest extensions NORMALIZE_WHITESPACE and ELLIPSIS are always on, so
this response also matches:

.. response::

   200 ...
   ...

   He...o
..

----

POST requests include the data to be posted after the request line.

.. request:: A simple POST

   POST /foo
   a=1&b=2
..

The simple application used in this self test always responds to POST
requests by echoing back the posted parameters:

.. response::

   You said: a=1 and b=2
..

Just like with GETs, you can match against headers and content or content only.

.. response::

   200 Ok
   Content-type: text/plain

   You said: a=1 and b=2
..

----

Fixture code may be run around a request.

.. request:: A special request requiring its own fixture.
   :setup: client.setup_special()
   :teardown: client.teardown_special()

   GET /special
..

.. response ::

   SPECIAL is set.
..

.. request:: Without the fixture
   
   GET /special
..

.. response::

   SPECIAL is not set.
..

----

A simple shell example.

.. shell :: echo "Hello"

   Hello
..

Source
~~~~~~

Here is the source of the fixtures file used with this test:

.. include:: about.py
   :literal:

And the source of the test document itself:

.. include:: about.rst
   :literal:
   
.. _`reStructured Text`: http://docutils.sourceforge.net/rst.html
.. _`paste.fixtures.TestApp` : http://pythonpaste.org/testing-applications.html