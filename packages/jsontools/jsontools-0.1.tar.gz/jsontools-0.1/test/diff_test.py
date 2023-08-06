
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

import pprint
import unittest

import simplejson

import jsontools

class DiffTest(unittest.TestCase):
    
    def do_compare(self, left, right):
        stream = StringIO()
        jsontools.jsondiff(left, right, stream=stream)
        stream.seek(0)
        result = jsontools.jsonapply(stream, left, in_place=False)
        self.assertEqual(jsontools.jsoncmp(right, result), True)
            
    def test_basic(self):
        data = """
            {"test": "foo"}
            {"test": "bar"}
            {"test": "foo"}
            {}
            [1, 2, 3]
            [2]
            {"bar":{"foo":2}}
            {"bar":{"foo":2}}
            {"bar":{"baz":2}}
            {"bar":{"bam":2}}
            {"foo":[1, 3, 2]}
            {"foo":[2, 3, 1]}
        """.strip().split('\n')
        tests = [(data[i], data[i+1]) for i in range(0, len(data), 2)]
        for t in tests:
            self.do_compare(simplejson.loads(t[0]), simplejson.loads(t[1]))

    def test_random(self):
        num_tests = 1000
        fj = jsontools.FuzzyJson()
        for obj in fj.generate(num_tests):
            ret = fj.modify(obj)
            self.do_compare(obj, fj.modify(obj))        
