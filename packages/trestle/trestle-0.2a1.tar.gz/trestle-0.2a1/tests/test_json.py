from nose.tools import assert_raises, assert_equal
from trestle.json import JSONOutputChecker, Decoder, Wild, odict
from simplejson import dumps

# mock example
class E:
    def __init__(self, want):
        self.want = want


def test_check_output():
    oc = JSONOutputChecker()
    assert not oc.check_output('[1, 2, 3]', 'hello', None)
    assert oc.check_output("[<any>]", "[1, 2, 3]", None)

    ex = dumps([1, [2, 3, 4], 5])
    assert oc.check_output('[<any>]', ex, None)
    assert oc.check_output('[<any>, 5]', ex, None)
    assert oc.check_output('[1, <any>]', ex, None)
    assert oc.check_output('[1, [2, <any>], 5]', ex, None)

    dex = dumps(odict([("1", 2), ("3", 4), ("five", "nine"),
                       ("six", ["a", "list"]),
                       ("seven", odict([("a", "b"), ("b", "c")]))]))
    assert oc.check_output('{<any>: <any>}', dex, None)
    assert oc.check_output(
        '{<any>: <any>, "six": ["a", <any>], "seven": <any>}', dex, None)

    assert oc.check_output('"..."', '"anything"', None)
    assert oc.check_output('{"...": 1}', '{"a key": 1}', None)

    assert not oc.check_output('{"not this": 1}', '{"but that": 2}', None)

    
def test_decoder():
    d = Decoder()
    w = d.decode("<any>")
    print w
    assert isinstance(w, Wild)
    assert w.tag == 'any'
    assert_raises(ValueError, lambda: d.decode("<any"))

    r = d.decode('{"a": 1, "b": <any>}')
    print r, r['b']
    assert_equal(r['b'].tag, 'any')

    r = d.decode('[<any>, 2, 3, <any>, "steve"]')
    print r
    assert_equal(r, [Wild(), 2, 3, Wild(), u"steve"])

    r = d.decode('{<any>: 2, "foo": "bar", "baz": <any>}')
    print r
    assert_equal(r, odict([(w, 2), ("foo", "bar"), ("baz", w)]))
    

def test_outputchecker_wildcard_list_elements():
    any = Wild()
    ex = [1, 2, 3, 4, 5]
    oc = JSONOutputChecker()
    assert oc.compare_objs(ex, ex)
    assert oc.compare_objs([any], ex)
    assert oc.compare_objs([any, 2, 3, 4, 5], ex)
    assert oc.compare_objs([any, 3, any], ex)
    assert oc.compare_objs([any, 5], ex)

    assert not oc.compare_objs([any], [])
    assert not oc.compare_objs([any, 5, any], ex)
    assert not oc.compare_objs([1, 2, any, 3, any], ex)    
    assert not oc.compare_objs([], ex)
    assert not oc.compare_objs([any, 4], ex)
    assert not oc.compare_objs([3, any], ex)
    assert not oc.compare_objs([any, 5, 6], ex)

    ex_nested = [1, [2, 3, 4], 5]
    assert oc.compare_objs(ex_nested, ex_nested)
    assert oc.compare_objs([any], ex_nested)
    assert oc.compare_objs([any, 5], ex_nested)
    assert oc.compare_objs([1, [2, any], 5], ex_nested)

    print "** mono"
    mono = [1, 1]
    assert oc.compare_objs([any, 1], mono)
    


def test_outputchecker_wildcard_dict_elements():
    any = Wild()
    ex = odict([("1", 2), ("3", 4), ("five", "nine"),
                ("six", ["a", "list"]),
                ("seven", odict([("a", "b"), ("b", "c")]))])
    oc = JSONOutputChecker()
    
    assert oc.compare_objs(ex, ex)
    assert oc.compare_objs(odict([(any, any)]), ex)
    assert oc.compare_objs(odict([(any, any),
                                  ("six", ["a", any]),
                                  ("seven", any)]), ex)

    # {<any>: 2} meaning any and all keys must have value of 2
    assert not oc.compare_objs(odict([(any, 2)]), ex)
    # {<any>: <any>, "six": [<any>, "a"], "seven": <any>}
    # does not match because terms in value for key "six" do
    # not match
    assert not oc.compare_objs(odict([(any, any),
                                      ("six", [any, "a"]),
                                      ("seven", any)]), ex)


def test_output_diff():
    oc = JSONOutputChecker()
    example = E("[]\n")
    got = "[1, 2, 3]"
    out = oc.output_difference(example, got, 0)
    print out
    assert 'Diff' in out

    example = E("[<any>]\n")
    out = oc.output_difference(example, got, 0)
    print out
