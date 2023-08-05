
import unittest, StringIO

import spoon
from spoon import ber

class testAllAttr(spoon.Serial):
    prop1 = "prop1"
    prop2 = "blah"
    def __init__(self):
        self.prop3 = 123

class testSerialProp(spoon.Serial):
    prop1 = spoon.serialprop()
    prop2 = "blah"
    def __init__(self):
        self.prop1 = "prop1"
        self.prop2 = 1234
        
class testLazyProp(spoon.Serial):
    prop1 = spoon.serialprop()
    prop2 = spoon.lazyprop()
    def __init__(self):
        self.prop1 = "blah"
        self.prop2 = "I'm Lazy"
        
class SpoonTest(unittest.TestCase):
    
    def test_1_encode_all(self):
        testObj = testAllAttr()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj)
        fd.seek(0)
        b = ber.BERStream(fd)
        result = b.next()
        self.assertEquals(result.prop1, testObj.prop1)
        self.assertEquals(result.prop2, testObj.prop2)
        self.assertEquals(result.prop3, testObj.prop3)
        
    def test_2_encode_some(self):
        testObj = testSerialProp()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj)
        fd.seek(0)
        b = ber.BERStream(fd)
        result = b.next()
        self.assertEquals(result.prop1, testObj.prop1)
        self.assertEquals(result.prop2, "blah")
        self.assertEquals(testObj.prop2, 1234)
    
    def test_3_encode_lazy(self):
        testObj = testLazyProp()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj)
        fd.seek(0)
        b = ber.BERStream(fd)
        result = b.next()
        self.assertEquals(result.prop1, testObj.prop1)
        # Check that the lazy props haven't been decoded.
        self.assertEquals(False, result._spoon_lazydata.closed)
        # Can't do this test anymore because of auto-decoding properties
        #self.assertEquals(result.prop2, None)
        #
        self.assertEquals(testObj.prop2, "I'm Lazy")
        # Check to see that we have decoded the lazy props
        self.assertEquals(result.prop2, "I'm Lazy")
        self.assertEquals(True, result._spoon_lazydata.closed)
    
    def test_4_reencode_lazy(self):
        testObj = testLazyProp()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj)
        fd.seek(0)
        b = ber.BERStream(fd)
        result = b.next()
        self.assertEquals(result._spoon_lazydata.closed, False)
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(result)
        fd.seek(0)
        b = ber.BERStream(fd)
        result2 = b.next()
        self.assertEquals(result2._spoon_lazydata.closed, False)
        self.assertEquals(result2.prop2, "I'm Lazy")
        self.assertEquals(result2._spoon_lazydata.closed, True)
        
    def test_5_encode_compress(self):
        testObj = testAllAttr()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj, True)
        fd.seek(0)
        b = ber.BERStream(fd)
        result = b.next()
        self.assertEquals(result.prop1, testObj.prop1)
        self.assertEquals(result.prop2, testObj.prop2)
        self.assertEquals(result.prop3, testObj.prop3)
    
    def test_6_encode_several(self):
        testObj1 = testAllAttr()
        testObj2 = testAllAttr()
        fd = StringIO.StringIO()
        b = ber.BERStream(fd)
        b.add(testObj1)
        b.add(testObj2)
        fd.seek(0)
        b = ber.BERStream(fd)
        result1 = b.next()
        self.assertEquals(result1.prop1, testObj1.prop1)
        self.assertEquals(result1.prop2, testObj1.prop2)
        self.assertEquals(result1.prop3, testObj1.prop3)
        b = ber.BERStream(fd)
        result2 = b.next()
        self.assertEquals(result2.prop1, testObj2.prop1)
        self.assertEquals(result2.prop2, testObj2.prop2)
        self.assertEquals(result2.prop3, testObj2.prop3)
        
