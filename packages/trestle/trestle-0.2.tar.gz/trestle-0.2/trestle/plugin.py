"""
Trestle -- doctest for RESTful services
---------------------------------------

Trestle is a plugin for nose that is used to make web service
documentation runnable. The documentation files must be in
reStructureText format, and include fixtures, request and response
sections, like this::

  .. fixtures:: test.fixtures

  The application used by this self test is very simple: it always
  replies with 'Hello' to GET requests. Let's start the test examples
  with a simple GET request.
  
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
  
  Just like with GETs, you can match against headers and content or content
  only.
  
  .. response::
  
    200 Ok
    Content-type: text/plain
  
    You said: a=1 and b=2  
  ..

A fixtures directive is required in every document to be tested. The
directive must name a python module. The module must include the
following:

client
  A client application to be called with methods .get(), .post(),
  .put(), etc. Each method must accept at least the arguments url and
  data, and may accept others but may not require
  them. paste.fixtures.TestApp is such a client, though it natively
  supports only .get() and .post().

And may include the following:

setup_all(cls)
  Setup fixture run before the first request.

teardown_all(cls)
  Teardown fixture run after the last request.

setup_each(inst)
  Setup fixture run before each request.

teardown_each(inst)
  Teardown fixture run after each request.

Each request to be sent to using the client defined in fixtures is
specified used a request block, like this::

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
"""

import os
import logging
import subprocess
from pkg_resources import resource_filename
import doctest as dt

from nose.plugins import Plugin
from nose.importer import add_path
from nose.util import resolve_name
from docutils.core import publish_doctree, publish_from_doctree
from docutils.parsers.rst import directives, convert_directive_function
from docutils import nodes
from textwrap import wrap

# for debugging
from nose.tools import set_trace

log = logging.getLogger(__name__)


class Trestle(Plugin):
    """
    Doctest for REST apps in ReST files. Parses reStructuredText
    documents looking for request and response sections, and
    constructs test examples that make the requests and expect to
    receive the response(s) defined for the requests. A fixtures file
    referenced by each reStructuredText document must be used to define
    class and test level fixtures, as well as the http client (or mock client)
    to be used to make the requests.
    """

    def options(self, parser, env=None):
        super(Trestle, self).options(parser, env)
        parser.add_option('--trestle-extension', action='store',
                          dest='trestle_extension', default='.rst',
                          help='Look for trestle tests in files with '
                          'this extension')
        parser.add_option('--trestle-css', action='store',
                          dest='trestle_css', default='css/rst.css',
                          help='Include this .css file in generated '
                          'html documentation files. Relative paths '
                          'are relative to the trestle package or your '
                          'working dir')
        parser.add_option('--trestle-output', action='store',
                          dest='trestle_output_dir', default='docs',
                          help='Output generated html documentation files '
                          'in this directory. Relative paths are relative '
                          'to your working dir.')

    def configure(self, options, conf):
        super(Trestle, self).configure(options, conf)
        if not self.enabled:
            return
        self.ext = options.trestle_extension
        self.css = options.trestle_css
        self.output_dir = os.path.abspath(options.trestle_output_dir)
        self.conf = conf
        self.docs = []

    def prepareTestLoader(self, loader):
        self.loader = loader

    def loadTestsFromFile(self, filename):
        if not filename.endswith(self.ext):
            return
        yield self.loader.loadTestsFromTestClass(self.createTestClass(filename))

    def report(self, stream):
        log.debug('trestle docs %s', self.docs)
        if not self.docs:
            return
        for filename, rst in self.docs:
            # update the examples in the document with
            # success/failure and the diff (if failed)
            #
            #set_trace()
            for node in rst.doc.traverse(lambda n: hasattr(n, 'example')):
                log.debug('found example node %s', node)
                example = node.example
                if example.passed:
                    node['classes'].append('pass')
                else:
                    # create a section node
                    # replace orig node with new
                    refid = str(hash(node))
                    parent = node.parent
                    sect = nodes.section()
                    sect['ids'] = [refid]
                    node['classes'].append('fail')
                    msg = nodes.literal_block(
                        example.message,
                        example.message, classes=['failure', 'output'])
                    txt = nodes.title()
                    txt.append(nodes.reference('', '', refid=refid))
                    sect.append(txt)
                    sect.append(node)
                    sect.append(msg)
                    parent.replace(node, sect)
                    self.addTocEntry(sect, example)
            self.writeDocs(filename, rst, stream)

    def addTocEntry(self, sect, example):
        enclosure = self.findSection(sect.parent)
        topic = self.findTocList(enclosure)
        if not topic:
            return

        title = nodes.Text("FAILED: %s" % example.description)
        reference = nodes.reference('', '', refid=sect['ids'][0],
                                    *(title,))
        ref_id = sect.document.set_id(reference)
        sect['refid'] = ref_id
        sect.document.ids[sect['ids'][0]] = sect
        entry = nodes.paragraph('', '', reference)
        item = nodes.list_item('', entry)
        item['classes'].append('fail')
        topic.append(item)

    def findTocList(self, section):
        id = section['ids'][0]
        doc = section.document
        try:
            cnt = doc.ids['contents']
        except KeyError:
            return
        refs = [r for r in
                cnt.traverse(lambda n: isinstance(n, nodes.reference))
                if r.get('refid') == id]
        if not refs:
            return
        ref = refs[0]
        top = ref.parent.parent.parent # the bullet-list
        if top.attributes.get('failures'):
            return top
        # find one that exists already
        blists = [n for n in top.children
                  if (isinstance(n, nodes.bullet_list)
                      and n.attributes.get('failures'))]
        if blists:
            return blists[0]
        # new one is needed
        new_blist = nodes.bullet_list()
        new_blist.attributes['failures'] = True
        ref.append(new_blist)
        return new_blist

    def findSection(self, node):
        if isinstance(node, nodes.section) or \
           isinstance(node, nodes.document):
            return node
        return self.findSection(node.parent)

    def writeDocs(self, filename, rst, stream):
        if not self.output_dir:
            return
        outfile = os.path.join(self.output_dir,
                               os.path.basename(filename)[:-4] + '.html')

        # css file paths may be relative to trestle or the working dir
        overrides = {}
        if self.css:
            if os.path.isabs(self.css):
                sheet = self.css
            else:
                local = os.path.abspath(self.css)
                if os.path.exists(local):
                    sheet = local
                else:
                    pkgd = resource_filename('trestle', self.css)
                    if os.path.exists(pkgd):
                        sheet = pkgd
                    else:
                        raise OSError("Unable to locate css file %s" % self.css)
            overrides['stylesheet_path'] = sheet

        res = publish_from_doctree(
            rst.doc, destination_path=outfile,
            writer_name='html',
            settings_overrides=overrides
            )

        if not os.path.isdir(self.output_dir):
            if os.path.isfile(self.output_dir):
                raise OSError("Output dir %s exists and is a file"
                              % self.output_dir)
            os.mkdir(self.output_dir)

        out = open(outfile, 'w')
        out.write(res)
        out.close()
        stream.writeln("Wrote trestle %s to %s" % (filename, outfile))

    def wantFile(self, filename):
        if filename.endswith(self.ext):
            return True

    def readFile(self, filename):
        return RstSuite(filename)

    def createTestClass(self, filename):
        """Create a test class for an rst file.

        The test class sets up the fixtures and yields a test for each example
        in the rst file.
        """
        rst = RstExampleReader(filename)
        self.docs.append((filename, rst))

        class RstTestClass(object):
            @classmethod
            def setup_class(cls):
                rst.setup_all(cls)

            @classmethod
            def teardown_class(cls):
                rst.teardown_all(cls)

            def setup(self):
                rst.setup(self)

            def teardown(self):
                rst.teardown(self)

            def test(self):
                client = rst.client()
                for example in rst.examples:
                    def case(client):
                        if example.setup is not None:
                            self._eval(example.setup,
                                       rst.fixture.__dict__)
                        try:
                            example(client)
                        finally:
                            if example.teardown is not None:
                                self._eval(example.teardown,
                                           rst.fixture.__dict__)
                    case.description = str(example)
                    yield case, client

            def _eval(self, eval_string, context):
                eval(eval_string, context)

        # put the test class in proper module context
        RstTestClass.__module__ = rst.fixture.__name__
        return RstTestClass


class RstExampleReader(object):
    """Read an .rst file, looking for 2 things:

    1. a fixture directive that indicates the module to load fixtures
       from. This is required and the module must at least define
       the client, that is the web client instance that will be
       passed to each Example to execute it.

    2. example directives, each of which becomes an Example instance,
       which is a runnable test that executes by using the client it
       is passed to call the method in the request, and expects the
       response received to match any following response directives.
    """
    def __init__(self, filename):
        self.fixture = None
        self.filename = filename
        self.examples = []
        directives.register_directive('fixtures', convert_directive_function(
            FixtureDirective(self)))
        directives.register_directive('request', convert_directive_function(
            RequestDirective(self)))
        directives.register_directive('response', convert_directive_function(
            ResponseDirective(self)))
        directives.register_directive('shell', convert_directive_function(
            ShellDirective(self)))
        self.doc = publish_doctree(open(filename, 'r').read(),
                                   source_path=filename)

    def setup_all(self, cls):
        self._run_fixt('setup_all', cls)

    def teardown_all(self, cls):
        self._run_fixt('teardown_all', cls)

    def setup(self, inst):
        self._run_fixt('setup_each', inst)

    def teardown(self, inst):
        self._run_fixt('teardown_each', inst)

    def _run_fixt(self, name, *arg):
        fixture = getattr(self, 'fixture', None)
        if fixture:
            fixt = getattr(fixture, name, None)
            if fixt:
                fixt(*arg)

    def client(self):
        try:
            return self.fixture.client
        except AttributeError, e:
            raise AttributeError(
                "Trestle test file %s does not defined a fixture, "
                "or the fixture does not define the client, "
                "or the fixture could not be loaded. (%s)"
                % (self.filename, e))


class Example(object):
    """A ReST service request and expected response(s)
    """
    passed = None
    message = "This example could not be executed"

    def __init__(self, filename, description, method, url, data,
                 setup=None, teardown=None):
        self.filename = filename
        self.description = description
        self.method = method
        self.url = url
        self.data = data
        self.want = []
        self.setup = setup
        self.teardown = teardown

    def __call__(self, client):
        func = getattr(client, self.method.lower())
        self.response = response = func(self.url, self.data)
        match, message = self.compare(response)
        self.passed = match
        self.message = message
        if not match:
            raise AssertionError("Failed example:\n\n%s" % message)

    def compare(self, response):
        class Ex:
            pass

        # switch to html/xml or json mode based on
        # response content type
        checker = header_checker = dt.OutputChecker()
        try:
            headers = dict([(k.lower(), v) for k, v in response.headers])
            if ('xml' in headers['content-type']
                or 'html' in headers['content-type']):
                from trestle import xml
                checker = xml.LXMLOutputChecker()
            elif headers['content-type'] == 'application/json':
                from trestle import json
                checker = json.JSONOutputChecker()
        except (AttributeError, KeyError, ImportError), e:
            log.error("Error loading checker: %s %s", response.headers, e)
            pass

        for w in self.want:
            # we need a fake example to pass to the doctest output checker
            ex = Ex()
            try:
                ix = w.index(u'')
                headers, content = w[:ix+1], w[ix+1:]
            except ValueError:
                headers, content = [], w
            headers = '\n'.join(headers)
            content = '\n'.join(content) + '\n'

            check_flags = dt.NORMALIZE_WHITESPACE|dt.ELLIPSIS
            report_flags = dt.REPORT_UDIFF
            if headers:
                got_headers = '\n'.join(
                    [response.full_status] +
                    ["%s: %s" % h for h in response.headers]) + '\n'
                # FIXME better to check headers without respect to case or order
                match = header_checker.check_output(
                    headers, got_headers, check_flags)
                if not match:
                    ex.want = headers
                    out = (False, header_checker.output_difference(
                        ex, got_headers, report_flags))
                    if response.full_status.startswith('50'):
                        # server error; caller probably wants to know about that
                        out = (out[0],
                               out[1] + "Server error:\n" +
                               response.normal_body)
                    return out
            match = checker.check_output(
                content, response.normal_body, check_flags)
            if not match:
                ex.want = content
                return (False, checker.output_difference(
                    ex, response.normal_body, report_flags))
        return (True, None)

    def __str__(self):
        return "%s: %s %s (%s)" % \
               (self.filename, self.method.upper(), self.url, self.description)


class ShellExample(Example):
    """
    Example that executes a shell command and checks the stdout output of the
    command against the expected response. Use a ShellDirective to create a
    ShellExample.
    """

    def __init__(self, filename, command, expect,
                 setup=None, teardown=None, cwd=None, post=None, stderr=False):
        self.filename = filename
        self.command = command
        self.description = command
        self.expect = expect
        self.setup = setup
        self.teardown = teardown
        self.cwd = cwd
        self.post = post
        self.stderr = stderr

    def __call__(self, client):
        p = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True,
            shell=True,
            cwd=self.cwd)

        returncode = p.wait()
        stdout, stderr = p.stdout.read(), p.stderr.read()
        if returncode != 0 or self.stderr:
            output = stderr
        else:
            output = stdout
        if self.post:
            output = self.post(output)
        match, message = self.compare(output)
        self.passed = match
        self.message = message

        if not self.passed:
            raise AssertionError("Failed example:\n\n%s" % self.message)

    def __str__(self):
        return "%s: %s" % (self.filename, self.command)

    def compare(self, output):
        class Ex:
            pass

        checker = dt.OutputChecker()
        check_flags = dt.NORMALIZE_WHITESPACE|dt.ELLIPSIS
        report_flags = dt.REPORT_UDIFF
        match = checker.check_output(self.expect, output, check_flags)
        if not match:
            ex = Ex()
            ex.want = self.expect + '\n'
            return (False,
                    checker.output_difference(ex, output, report_flags))
        return (True, None)


class Directive(object):
    """Base class for following directives
    """
    arguments = (1, 0, True)
    content = True

    def __init__(self, suite):
        self.suite = suite

    def __call__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        # FIXME for debugging
        print self.__class__.__name__, name, arguments, options, \
              content, lineno


class FixtureDirective(Directive):
    """Directive that loads the fixture module and sets suite.fixture to that
    module.
    """
    def __call__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        name = str(arguments[0]).strip()
        # Add file dir to paths before attempting to load the
        # fixture
        add_path(os.path.dirname(self.suite.filename))
        self.suite.fixture = resolve_name(name)
        log.debug('called %s fixt %s', name, self.suite.fixture)
        return []


class RequestDirective(Directive):
    """Directive that reads a request section and creates
    a new Example. The example is appended to suite.examples.

    The request directive should include a useful description on the same line
    as the directive. This will become the test name when using verbose
    output. If the request requires custom fixtures, include these as options
    following the directive line and preceding the body of the directive. The
    fixtures will be evaluated in the context of the fixture module assigned
    by the ``.. fixtures`` directive.

    In the body of the directive, you may specify request headers, the request
    line, and any data to be sent with the request, in that order. If you do
    include headers in the request, separate the headers from the request line
    with a blank line,

    Examples:

    .. request :: A simple request

       GET /
    ..

    .. request :: Request with fixtures
       :setup: run_this()
       :teardown: run_that()

       GET /something
    ..

    .. request :: A request with POST data and headers

       Host: www.foobar.com
       Accept: text/xml

       POST /baz
       a=1&b=2
    ..

    Remember to indent the body, and always end with '..' alone on a line, to
    avoid parse errors.
    """
    options = {'setup': directives.unchanged,
               'teardown': directives.unchanged}
    def __call__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        description = arguments[0]
        if not content:
            error = state_machine.reporter.error(
                "request %s has no content; is there a space after the last "
                "argument, before the method and url?" % description)
            return [error]
        method, url = content.pop(0).split(' ')

        # FIXME look for blank line in content to split out headers

        # allow trailing backslashes on url line (makes
        # long urls more readable)
        while content and url.endswith('\\'):
            url = url[:-1] + content.pop(0).strip()

        # FIXME allow override of default encoding
        text = '\n'.join(content).encode('utf-8')
        if content:
            data = text
        else:
            data = None
        ex = Example(self.suite.filename, description, method, url, data,
                     setup=options.get('setup'),
                     teardown=options.get('teardown'))
        self.suite.examples.append(ex)
        call = "%s %s" % (method, url)
        out = nodes.literal_block(
            '', '',
            nodes.literal(method, method, classes=['request', 'method']),
            nodes.Text(' '),
            nodes.literal(url, url, classes=['request', 'url']),
            )
        if text:
            # wrap long lines?
            # FIXME wrap size should be configurable
            text = '\n\n' + text
            out += nodes.Text(text, text)
        return [out, nodes.caption(description, description)]


class ResponseDirective(Directive):
    """Directive that adds an expected response to the current
    example.

    Use this directive to add an expected response to match against the
    request most recently defined in the test document.

    You may match against response headers and content, or content only. To
    match against both headers and content, separate the headers from the
    content with a blank line.

    Examples:

    .. response ::

       200 OK
       Content-Type: text/plain
       ...

       Hello
    ..

    .. response ::

       This is just content
    ..
    """
    arguments = (0, 0, False)
    def __call__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        ex = self.suite.examples[-1]
        ex.want.append(content)

        # FIXME break long lines
        text = '\n'.join(content)
        node = nodes.literal_block(text, text, classes=['response'])
        node.example = ex
        return [node]


class ShellDirective(Directive):
    """
    Directive that creates a ShellExample. Format the directive with the
    shell command on the same line as the directive and the expected stdout
    output in the body of the directive:

    .. shell :: echo "Hello"

      Hello
    ..

    Remember to indent the body, and always end with '..' alone on a line, to
    avoid parse errors.
    """
    options = {'setup': directives.unchanged,
               'teardown': directives.unchanged,
               'cwd': directives.unchanged,
               'post': directives.unchanged,
               'stderr': directives.flag}
    def __call__(self, name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
        command = arguments[0]
        log.debug('shell command %s', command)
        if options.get('cwd'):
            log.debug('command will run in dir %s', options.get('cwd'))
        if not content:
            error = state_machine.reporter.error(
                "shell %s has no expected output; "
                "is there a space after the last "
                "argument, before the method and url?" % command)
            return [error]

        # FIXME allow overriding default encoding
        expect = '\n'.join(content).encode('utf-8')
        log.debug('command expects %s', expect)

        if options.get('post'):
            post = eval(options.get('post'), self.suite.fixture.__dict__)
        else:
            post = None

        ex = ShellExample(self.suite.filename, command, expect,
                          setup=options.get('setup'),
                          teardown=options.get('teardown'),
                          cwd=options.get('cwd'),
                          post=post,
                          stderr=('stderr' in options))
        self.suite.examples.append(ex)

        out = nodes.literal_block(
            '', '',
            nodes.literal(command, command, classes=['request', 'method'])
            )
        response = nodes.literal_block(expect, expect, classes=['response'])
        response.example = ex
        return [out, response]
