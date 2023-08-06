import ConfigParser
import StringIO

import mailprocess.main

def _make_test_factory(name, data):
    class TestFactory(object):
        test_factory = True
        def __init__(self, **kwargs):
            data[name] = kwargs
        def __call__(self):
            data[name]['__called__'] = True
    return TestFactory

_data = {}
_one = _make_test_factory('one', _data)
_two = _make_test_factory('two', _data)
_three = _make_test_factory('three', _data)
_four = _make_test_factory('four', _data)

def test_config():
    config = """\
[mailprocess]
start = one two

[one]
factory = mailprocess.tests:_one
arg1 = one
arg2 = two
next = three

[two]
factory = mailprocess.tests:_two
arg3 = three
arg4 = four
next = three

[three]
factory = mailprocess.tests:_three
arg5 = five
next = four

[four]
factory = mailprocess.tests:_four
arg6 = six
"""
    parser = ConfigParser.ConfigParser()
    parser.readfp(StringIO.StringIO(config))
    mailprocess.main.start(parser)
    assert(sorted(_data['one'].keys()), ('arg1', 'arg2', 'next'))
    assert(sorted(_data['two'].keys()), ('arg3', 'arg4', 'next'))
    assert(sorted(_data['three'].keys()), ('arg5', 'next'))
    assert(_data['four'] == {'arg6': 'six'})
    assert(_data['one']['next'] is _data['two']['next'])
    assert(_data['one']['next'] is not _data['three']['next'])
    assert(hasattr(_data['one']['next'], 'test_factory'))
    assert(_data['one'].get('__called__'))
    assert(_data['two'].get('__called__'))
    assert(not _data['three'].get('__called__'))
