"""
Tests for pickling arbitrary Objective-C objects

TODO:
- finish 'test' methods in this file
- tests for objects that implement old-style archiving
"""
import objc.test 
import pickle, cPickle, os

from objc.test.fnd import NSData, NSMutableData, NSString
from objc.test.fnd import NSArray, NSMutableArray, NSObject
from objc.test.fnd import NSKeyedArchiver, NSKeyedUnarchiver
from objc.test.fnd import NSDictionary, NSMutableDictionary

from objc.test.pickling import OC_Codable

# Update metadata for testing
objc.registerMetaDataForSelector("NSData", "dataWithBytes:length:",
    dict(
        arguments={
            2: dict(c_array_length_in_arg=3, type_modifier='n'),
        }
    ))


class NoCoding (objc.test.TestCase):
    # Test cases for pickling objects that don't
    # implement NSCoding

    # Disable stderr during these tests, otherwise garbage gets logged.
    def setUp(self):
        self._fd = os.dup(2)
        fd = os.open('/dev/null', os.O_WRONLY)
        os.dup2(fd, 2)
        os.close(fd)

    def tearDown(self):
        os.dup2(self._fd, 2)
        os.close(self._fd)
    def archive(self, value):
        return pickle.dumps(value)

    def unarchive(self, buffer):
        return pickle.loads(buffer)

    def assertBuffer(self, buffer):
        self.failUnless(isinstance(buffer, str))

    def testArchiveNSObject(self):
        i = NSObject.alloc().init()

        try:
            pickle.dumps(i)
        except (ValueError,):
            pass

        else:
            self.fail()

    def testArchiveNSObjectInArray(self):
        i = NSArray.arrayWithObject_(NSObject.alloc().init())

        try:
            pickle.dumps(i)
        except (ValueError,):
            pass

        else:
            self.fail()

class CodingObjC (objc.test.TestCase):
    # Test cases for pickling pure Objective-C
    # object graphs
    def archive(self, value):
        return pickle.dumps(value)

    def unarchive(self, buffer):
        return pickle.loads(buffer)

    def assertBuffer(self, buffer):
        self.failUnless(isinstance(buffer, str))

    def testNSData(self):
        i = NSData.dataWithBytes_length_('hello', 5)
        self.assertRaises(AttributeError, getattr, i, 'setLength_')
        buf = self.archive(i)
        self.assertBuffer(buf)


        o = self.unarchive(buf)
        self.assert_(isinstance(o, NSData))

        # XXX: this fails when using NSKeyedArchiver???
        #try:
        #    o.setLength_(0)
#
#        except (AttributeError,):
#            pass
#
#        else:
#            self.fail()
        #self.assertRaises(AttributeError, getattr, o, 'setLength_')

    def testNSMutableData(self):
        i = NSMutableData.dataWithBytes_length_('hello', 5)
        buf = self.archive(i)
        self.assertBuffer(buf)

        o = self.unarchive(buf)
        self.assert_(isinstance(o, NSData))
        o.setLength_(0)

    def testSimpleFields(self):
        i = OC_Codable.alloc().init()
        i._.floatValue = 2.5
        i._.doubleValue = 1.245
        i._.intValue = 99
        i._.int64Value = 2 ** 40

        buf = self.archive(i)
        self.assertBuffer(buf)

        o = self.unarchive(buf)
        self.assert_(isinstance(o, OC_Codable))
        self.assertEquals(o.floatValue(), 2.5)
        self.assertEquals(o.doubleValue(), 1.245)
        self.assertEquals(o.intValue(), 99)
        self.assertEquals(o.int64Value(), 2 ** 40)


    def testNSArray(self):
        i = OC_Codable.alloc().init()
        i._.floatValue = 2.5
        i._.doubleValue = 1.245
        i._.intValue = 99
        i._.int64Value = 2 ** 40

        a = NSArray.arrayWithArray_([i, i])

        buf = self.archive(a)
        self.assertBuffer(buf)

        o = self.unarchive(buf)
        self.assert_(isinstance(o, NSArray))
        self.assertEquals(len(o), 2)
        self.assert_(o[0] is o[1])
        self.assert_(isinstance(o[0], OC_Codable))

        self.assertEquals(o[0].floatValue(), 2.5)
        self.assertEquals(o[0].doubleValue(), 1.245)
        self.assertEquals(o[0].intValue(), 99)
        self.assertEquals(o[0].int64Value(), 2 ** 40)

    def testNSDictionar(self):
        s = NSString.stringWithString_(u"hello")
        i = OC_Codable.alloc().init()
        i._.floatValue = 2.5
        i._.doubleValue = 1.245
        i._.intValue = 99
        i._.int64Value = 2 ** 40

        d = NSDictionary.dictionaryWithDictionary_({s: i})
        self.failUnless(isinstance(d, NSDictionary))

        buf = self.archive(d)
        self.assertBuffer(buf)

        o = self.unarchive(buf)
        self.failUnless(isinstance(o, NSDictionary))
        self.failUnless(len(o) == 1)
        
        item = o[u'hello']
        self.failUnless(isinstance(item, OC_Codable))

    def dont_testNested(self):
        # The test below checks if self-recursive objects can be archived
        # and unarchived. 
        # This test is disabled because the object graphs cannot be 
        # reconstructed using NSKeyedArchiver/NSKeyedUnarchiver either.
        obj = OC_Codable.alloc().init()
        obj._.floatValue = 2.5
        obj._.doubleValue = 1.245
        obj._.intValue = 99
        obj._.int64Value = 2 ** 40

        lst = NSMutableArray.arrayWithArray_([obj, obj])
        lst.append(lst)

        buf = self.archive(lst)
        self.assertBuffer(buf)
        o = self.unarchive(buf)
        self.failUnless(isinstance(o, NSMutableArray))
        self.failUnless(len(o) == 3)
        self.failUnless(o[-1] is o)

        return

        key1 = NSString.stringWithString_("key1")
        key2 = NSString.stringWithString_("key2")

        dct = NSMutableDictionary.dictionaryWithDictionary_(
                { key1: lst })
        dct[key2] = dct

        buf = self.archive(dct)
        self.assertBuffer(buf)

        o = self.unarchive(buf)
        self.failUnless(isinstance(o, NSMutableDictionary))
        self.failUnless(isinstance(o[key2], NSMutableDictionary))
        self.failUnless(o[key2] is o)


    def testReferences(self):
        a = OC_Codable.alloc().init()
        i = OC_Codable.alloc().init()
        i.setIdValue_(a)

        buf = self.archive(i)
        self.assertBuffer(buf)
        o = self.unarchive(buf)

        self.failUnless(isinstance(o, OC_Codable))
        self.failUnless(isinstance(o.idValue(), OC_Codable))
        self.failIf(o.idValue() is o)
            
    def dont_testSelfReferential(self):
        # This doesn't actually work in Python::
        #
        #    import pickle
        # 
        #   def restore(o):
        #       return o
        #
        #    class MyObject (object):
        #       def __reduce__(self):
        #           return restore, (1, 2, {'o':self})
        #
        #    print pickle.dumps(MyObject())
        # 
        # We might be able to partially work around this by
        # treating NS<Collection> objects specially, but I'm 
        # afraid we're hosed for the general case...

        # XXX: might be able to recover lists

        # Direct
        i = OC_Codable.alloc().init()
        i.setIdValue_(i)

        buf = self.archive(i)
        self.assertBuffer(buf)
        o = self.unarchive(buf)

        self.failUnless(isinstance(o, OC_Codable))
        self.failUnless(o.idValue() is o)

        # Intermediate object

        a = OC_Codable.alloc().init()
        i = OC_Codable.alloc().init()
        a.setIdValue_(i)
        i.setIdValue_(a)

        self.failUnless(i.idValue().idValue() is i)

        buf = self.archive(i)
        self.assertBuffer(buf)
        o = self.unarchive(buf)

        self.failUnless(isinstance(o, OC_Codable))
        self.failUnless(o.idValue().idValue() is o)


        # Intermediate collection

        i = OC_Codable.alloc().init()
        i.setIdValue_(NSArray.arrayWithObject_(i))

        self.failUnless(i.idValue()[0] is i)

        buf = self.archive(i)
        self.assertBuffer(buf)
        o = self.unarchive(buf)

        self.failUnless(isinstance(o, OC_Codable))
        self.failUnless(o.idValue()[0] is o)

class MixedCoding (objc.test.TestCase):
    # Tests for object graphs that include Python
    # objects, both "pure" python objects and
    # subclasses of NSObject
    # Also: def __reduce__, def __reduce_ex__

    def archive(self, value):
        return pickle.dumps(value)

    def unarchive(self, buffer):
        return pickle.loads(buffer)

    def assertBuffer(self, buffer):
        self.failUnless(isinstance(buffer, str))


    def testPythonCoding(self):
        # Python object that implements NSCoding
        pass

    def testPythonNoCoding(self):
        # Python object that does not implement NSCoding
        pass

    def testPythonReduce(self):
        # Python object that implements __reduce__
        pass

    def testPythonReduceEx(self):
        # Python object that implements __reduce_ex__
        pass

    def testMixedGraphObjC(self):
        # NSDictionary containing list containing ObjC Object and Python object
        pass

    def testMixedGraphPython(self):
        # Python object with an ObjCObject as property
        pass



# Variant of CodingObjC that ensures that serializing/deserializing works
# when using a real NSKeyedArchiver.

class aCodingObjC (CodingObjC):
    def archive(self, value):
        return NSKeyedArchiver.archivedDataWithRootObject_(value)

    def unarchive(self, buffer):
        return NSKeyedUnarchiver.unarchiveObjectWithData_(buffer)

    def assertBuffer(self, buffer):
        self.failUnless(isinstance(buffer, NSData))

# Variants of the tests earlier in this file, now using
# cPickle instead of pickle.



class cNoCoding (NoCoding):
    def archive(self, value):
        return cPickle.dumps(value)

    def unarchive(self, buffer):
        return cPickle.loads(buffer)


class cCodingObjC (CodingObjC):
    def archive(self, value):
        return cPickle.dumps(value)

    def unarchive(self, buffer):
        return cPickle.loads(buffer)


class cMixedCoding (MixedCoding):
    def archive(self, value):
        return cPickle.dumps(value)

    def unarchive(self, buffer):
        return cPickle.loads(buffer)

if __name__ == "__main__":
    objc.test.main()
