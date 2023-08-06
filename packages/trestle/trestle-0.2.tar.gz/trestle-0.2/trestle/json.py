"""
json support based on simplejson by Bob Ippolito

simplejson is Copyright (c) 2006 Bob Ippolito

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import re
from simplejson.decoder import JSONArray, JSONString, JSONConstant, \
     JSONNumber, JSONDecoder, WHITESPACE, scanstring, errmsg
from simplejson.scanner import pattern, Scanner
from simplejson import decoder, dumps, loads
from difflib import ndiff
import doctest as dt
from pprint import pprint
from StringIO import StringIO


OutputChecker = dt.OutputChecker


# singleton representing the end of a list
class sng(object):
    def __init__(self, n):
        self.n = n
    def __str__(self):
        return self.n
    def __repr__(self):
        return self.n
eol = sng('eol')


class JSONOutputChecker(OutputChecker):

    def check_output(self, want, got, optionflags):
        parser = self.get_parser(want, got, optionflags)
        if not parser:
            return OutputChecker.check_output(
                self, want, got, optionflags)
        try:
            want_obj = parser(want)
            got_obj = parser(got)
        except ValueError:
            return False
        return self.compare_objs(want_obj, got_obj)

    def get_parser(self, want, got, optionflags):
        return self.loads

    def loads(self, json_string):
        return loads(json_string, cls=Decoder)

    def compare_objs(self, want, got):
        if want == got:
            return True
        if isinstance(want, Wild) and want.match(got):
            return True
        if isinstance(want, basestring):
            return self.compare_string(want, got)
        if isinstance(want, list):
            return self.compare_list(want, got)
        if isinstance(want, dict):
            return self.compare_dict(want, got)
        return False

    def compare_string(self, want, got):
        if "..." in want:
            pat = want.replace("...", r'.*')
            return re.search(pat, got)
        else:
            return want == got

    def compare_list(self, want, got):
        if not isinstance(got, list):
            return False
        if want == got:
            return True
        want_next = iter(want).next
        got_next = iter(got).next
        while True:
            try:
                this = want_next()
            except StopIteration:
                this = eol
            try:
                other = got_next()
            except:
                other = eol
            # end of both lists
            if this == other and this is eol:
                return True
            # term that does not match
            if not self.compare_objs(this, other):
                return False
            if isinstance(this, Wild):
                # consume other until other ends
                # or next in this matches other
                if other is eol:
                    # wildcards have to match *something*;
                    # eol is nothing
                    return False            
                try:
                    this_guard = want_next()
                except StopIteration:
                    this_guard = eol
                #if self.compare_objs(this_guard, other):
                #    continue
                while True:
                    try:
                        other = got_next()
                    except StopIteration:
                        other = eol
                    if other is eol and this_guard is not eol:
                        # I had more left, the other ran out
                        return False
                    if not self.compare_objs(this_guard, other):
                        continue
                    # consumed up to a match
                    break                            

    def compare_dict(self, want, got):
        if not isinstance(got, dict):
            return False
        return self.compare_list(want.keys(), got.keys()) \
               and self.compare_list(want.values(), got.values())
        
    def output_difference(self, example, got, optionflags):
        want = example.want
        parser = self.get_parser(want, got, optionflags)
        errors = []
        if parser is not None:
            try:
                want_obj = parser(want)
            except ValueError, e:
                errors.append("In example: %s" % e)
            try:
                got_obj = parser(got)
            except ValueError, e:
                errors.append("In actual output: %s" % e)
        if parser is None or errors:
            value = OutputChecker.output_difference(
                self, example, got, optionflags)
            if errors:
                errors.append(value)
                return '\n'.join(errors)
            else:
                return value
        diff_parts = []
        diff_parts.append('Expected:')

        lines = [ "  " + l for l in self.pprint(want_obj).split("\n")]
        diff_parts.extend(lines)
        diff_parts.append('Got:')
        lines = [ "  " + l for l in self.pprint(got_obj).split("\n")]
        diff_parts.extend(lines)
        diff_parts.append('Diff:')
        diff = [ "  " + l for l in self.collect_diff(want_obj, got_obj)]
        diff_parts.extend(diff)
        return '\n'.join(diff_parts)

    def collect_diff(self, want, got):
        if type(want) != type(got) \
               and not issubclass(want, got) \
               and not issubclass(got, want):
            return ["Expected a %s, got a %s" % (type(want), type(got))]
        want_lines = self.pprint(want).split("\n")
        got_lines = self.pprint(got).split("\n")
        return ndiff(want_lines, got_lines)

    def collect_list_diff(self, want, got):
        return ndiff(want, got)

    def pprint(self, obj):
        stream = StringIO()
        pprint(obj, stream=stream)
        return stream.getvalue()


@pattern(r'{')
def JSONObject(match, context, _w=WHITESPACE.match):
    """
    Same as simplejson.decoder.JSONObject, except uses an ordered dict
    (based on nose.util.odict) as the internal representation.
    """
    pairs = odict()
    s = match.string
    end = _w(s, match.end()).end()
    nextchar = s[end:end + 1]
    # trivial empty object
    if nextchar == '}':
        return pairs, end + 1
    if nextchar not in ('"', '<'):
        raise ValueError(errmsg("Expecting property name or wildcard", s, end))
    end += 1
    encoding = getattr(context, 'encoding', None)
    iterscan = JSONScanner.iterscan
    while True:
        if nextchar == '<':
            # scan up to >
            tagstart = end
            end = s.index('>', end)
            key = Wild(s[tagstart:end])
            end += 1
        else:
            key, end = scanstring(s, end, encoding)
        end = _w(s, end).end()
        if s[end:end + 1] != ':':
            raise ValueError(errmsg("Expecting : delimiter", s, end))
        end = _w(s, end + 1).end()
        try:
            value, end = iterscan(s, idx=end, context=context).next()
        except StopIteration:
            raise ValueError(errmsg("Expecting object", s, end))
        pairs[key] = value
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar == '}':
            break
        if nextchar != ',':
            raise ValueError(errmsg("Expecting , delimiter", s, end - 1))
        end = _w(s, end).end()
        nextchar = s[end:end + 1]
        end += 1
        if nextchar not in ('"', '<'):
            raise ValueError(errmsg("Expecting property name or wildcard",
                                    s, end - 1))
    object_hook = getattr(context, 'object_hook', None)
    if object_hook is not None:
        pairs = object_hook(pairs)
    return pairs, end


@pattern(r'<([^>]+)')
def JSONWildCard(match, context, _w=WHITESPACE.match):
    s = match.string
    end = _w(s, match.end()).end()
    nextchar = s[end:end+1]
    if nextchar == '>':
        return Wild(match.group()[1:]), end + 1
    raise ValueError(errmsg("Expecting end of wildcard tag", s, end - 1))
    


TERMS = [
    JSONObject,
    JSONWildCard,
    JSONArray,
    JSONString,
    JSONConstant,
    JSONNumber
    ]
JSONScanner = Scanner(TERMS)


class Decoder(JSONDecoder):
    _scanner = Scanner(TERMS)

    def raw_decode(self, s, **kw):
        # patch in updated decoder?
        _S = decoder.JSONScanner
        decoder.JSONScanner = JSONScanner
        try:
            # do stuff
            return JSONDecoder.raw_decode(self, s, **kw)
        finally:
            # unpatch
            decoder.JSONScanner = _S
  

class Wild:
    """
    Basic wildcard. With tag of 'any', matches anything.

    >>> w = Wild()
    >>> w.match("hello")
    True
    >>> w.match(1)
    True

    With tag of 'timestamp', matches contiguous sets of 6 or more digits.

    >>> t = Wild('timestamp')
    >>> t.match(12345666)
    True
    >>> t.match('123234343')
    True
    >>> t.match('123')
    False
    """
    _re = {'timestamp': re.compile('\d{6,}')}
    
    def __init__(self, tag='any'):
        self.tag = tag

    def match(self, other):
        if self.tag == 'any':
            return True
        else:
            try:
                return self._re[self.tag].search(str(other)) is not None
            except KeyError:
                raise ValueError("Unknown wildcard type '%s'" % self.tag)
            except TypeError:
                pass
        return False

    @classmethod
    def register(cls, tag, regex):
        """
        Register a new wildcard name.

        To register a new wildcard type, call Wild.register(tag, regex).

        >>> Wild.register('nutlike', '[Nn][Uu][Tt]')
        >>> n = Wild('nutlike')
        >>> n.match('peanut')
        True
        >>> n.match('walnut')
        True
        >>> n.match('split pea soup')
        False
        """
        cls._re[tag] = re.compile(regex)
    
    def __eq__(self, other):
        try:
            return self.tag == other.tag
        except AttributeError:
            return False
    
    def __hash__(self):
        return hash(self.tag)

    def __str__(self):
        return '<%s>' % self.tag

    def __repr__(self):
        return '<%s>' % self.tag

    
    
# Adds iteritems to nose.util.odict, corrects __init__
# to actually work
class odict(dict):
    """Simple ordered dict implementation, based on:

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/107747
    """
    def __init__(self, *arg, **kw):
        self._keys = []
        for item in arg:
            self.update(item)
        self.update(kw)
        super(odict, self).__init__()

    def __delitem__(self, key):
        super(odict, self).__delitem__(key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        super(odict, self).__setitem__(key, item)
        if key not in self._keys:
            self._keys.append(key)

    def __str__(self):
        return "{%s}" % ', '.join(["%r: %r" % (k, v) for k, v in self.items()])

    def clear(self):
        super(odict, self).clear()
        self._keys = []

    def copy(self):
        d = super(odict, self).copy()
        d._keys = self._keys[:]
        return d

    def items(self):
        return presorted(zip(self._keys, self.values()))

    def iteritems(self):
        for k in self._keys:
            yield k, self[k]

    def keys(self):
        return presorted(self._keys[:])

    def setdefault(self, key, failobj=None):
        item = super(odict, self).setdefault(key, failobj)
        if key not in self._keys:
            self._keys.append(key)
        return item

    def update(self, term):
        try:
            for key in term.keys():
                self[key] = term[key]
        except AttributeError:
            for key, value in term:
                self[key] = value
                
    def values(self):
        return map(self.get, self._keys)


class presorted(list):
    """
    A list that has been presorted and can't be resorted. This is used to
    keep odict items() and keys() in their sorted order.
    """
    def sort(self):
        pass
