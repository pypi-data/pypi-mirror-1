"""
This module implements a structure comparer

>>> da  = {1:"a"}
>>> dict_compare(da,da)
True
>>> dab = {1:"a",2:"b"}
>>> dict_compare(da,dab)
False
>>> dict_compare(dab,da)
False
>>> da2  = {1:"A"}
>>> dict_compare(da,da2)
False

# Probando con datos con tuples []
>>> sr = SimpleReporter()
>>> db   = {1:['foo', 'bar']}
>>> dict_compare(db,db,sr)
True
>>> sr.get_errors()

>>> sr = SimpleReporter()
>>> db2  = {1:['bar', 'foo']}
>>> dict_compare(db,db2,sr)
False
>>> len(sr.get_errors())
60

>>> sr = SimpleReporter()
>>> dc   = ['a', {'foo': 'bar'}]
>>> dict_compare(dc,dc,sr)
True
>>> dc2  = ['b', {'foo': 'bar'}]
>>> dict_compare(dc,dc2,sr)
False
>>> len(sr.get_errors())
38

>>> sr  = SimpleReporter()
>>> dd  = ['a']
>>> dd2 = {'k': 'v'}
>>> dict_compare(dd,dd2,sr)
False
>>> len(sr.get_errors())
60
"""
import sys
import os

def listToDict(l):
    d = {}
    for (k,v) in enumerate(l):
        d[k] = v
    return d

def reportNotFoundKeysIn(d1,d2,label):
    if isinstance(d1, (list, tuple)):
        d1 = listToDict(d1)
        d2 = listToDict(d2)
    difference = dict( [(key,value) for key,value in d1.iteritems() if not key in d2] )
    if difference:
        return label + str( difference ) + os.linesep
    else:
        return ""

def dict_compare(d_expected, d_received, reporter=None):
    if cmp(d_expected,d_received)==0:
        return True
    if reporter != None:
        msg = ""
        if type(d_expected) == type(d_received):
            msg += reportNotFoundKeysIn(d_expected,d_received,"Not In Received: ")
            msg += reportNotFoundKeysIn(d_received,d_expected,"Not In Expected: ")
            # report keys with different values
            differentKeysLabelShown = False
            if isinstance(d_expected, (list, tuple)):
                d_expected = listToDict(d_expected)
                d_received = listToDict(d_received)
            for expected_key in d_expected.keys():
                if expected_key in d_received:
                    if d_expected[expected_key] != d_received[expected_key]:
                        if not differentKeysLabelShown:
                            msg += "Different values in"+os.linesep
                        msg += "'%s':  %s != %s " % (   repr(expected_key),
                                                        repr(d_expected[expected_key]),
                                                        repr(d_received[expected_key])) + os.linesep
        else:
            msg += ( "Not same type: "
                     + repr(d_expected)+ repr(type(d_expected)) + " != "
                     + repr(d_received)+ repr(type(d_received)) )
        reporter(msg)
                    
    return False

class SimpleReporter(object):
    def __init__(self):
        self._msg = None
    def __call__(self, msg):
        self._msg = msg
    def get_errors(self):
        return self._msg

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

