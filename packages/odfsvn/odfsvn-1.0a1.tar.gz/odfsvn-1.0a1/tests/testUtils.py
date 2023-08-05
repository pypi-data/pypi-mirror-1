import os
import shutil
import tempfile
from unittest import TestCase
from odfsvn.utils import ensureDirectoryExists
from odfsvn.utils import getXmlInfo
from odfsvn.utils import withTempDirectory
from xml.dom import minidom

class getXmlInfoTests(TestCase):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
             <root>
               <elem title="element">elem content</elem>
               <empty/>
               <container>
                 <child id="one">child one content</child>
                 <child id="two">child two content</child>
               </container>
             </root>
             """

    def setUp(self):
        self.dom=minidom.parseString(self.xml)

    def testElementContent(self):
        self.assertEqual(getXmlInfo(self.dom, "elem"), "elem content")

    def testEmptyElementContent(self):
        self.assertEqual(getXmlInfo(self.dom, "empty"), "")

    def testMissingElement(self):
        self.assertRaises(KeyError, getXmlInfo, self.dom, "missing")

    def testElementAttribute(self):
        self.assertEqual(getXmlInfo(self.dom, "elem", "title"), "element")

    def testMissingAttribute(self):
        # XXX This is a bit of an API wart: unlike missing elements a
        # missing attribute does not raise a KeyError. This is due to
        # XML minidom getAttribute() returning an empty string for a missing
        # attribute.
        self.assertEqual(getXmlInfo(self.dom, "elem", "missing"), "")

    def testNestedElement(self):
        self.assertEqual(getXmlInfo(self.dom, "child"), "child one content")

    def testNestedAttribute(self):
        self.assertEqual(getXmlInfo(self.dom, "child", "id"), "one")



class withTempDirectoryTests(TestCase):
    def setUp(self):
        self.call=None
        def func(*args, **kwargs):
            self.call=(args, kwargs)
        self.func=func
        self.wrapped=withTempDirectory(self.func)

    def testTempdirParameterPassedOn(self):
        self.wrapped(tempdir="/one/two/three")
        self.assertEqual(self.call, ((), dict(tempdir="/one/two/three")))

    def testTempdirParameterPassed(self):
        self.wrapped()
        self.assertEqual(self.call[0], ())
        self.failUnless("tempdir" in self.call[1])

    def testGivenTempdirNotCreated(self):
        def func(self, tempdir):
            self.failIf(os.path.exists(tempdir))
        withTempDirectory(func)(self, tempdir="/one/two/three")

    def testTempdirCreatedAndRemoved(self):
        notes={}
        def func(self, tempdir):
            notes["dir"]=tempdir
            self.failUnless(os.path.isdir(tempdir))
        withTempDirectory(func)(self)
        self.failIf(os.path.exists(notes["dir"]))



        
class ensureDirectoryExistsTests(TestCase):
    def setUp(self):
        self.basepath=tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.basepath)

    def testEmptyPath(self):
        ensureDirectoryExists(self.basepath, [])
        self.assertEqual(os.listdir(self.basepath), [])

    def testSkipSeenPaths(self):
        ensureDirectoryExists(self.basepath, ["skip"],
                [os.path.join(self.basepath, "skip")])
        self.assertEqual(os.listdir(self.basepath), [])

    def testSinglePathAdd(self):
        seen=set()
        ensureDirectoryExists(self.basepath, ["todo"], seen)
        self.assertEqual(seen, set([os.path.join(self.basepath, "todo")]))
        self.assertEqual(os.listdir(self.basepath),["todo"])

    def testDuplicatePathAdd(self):
        seen=set()
        ensureDirectoryExists(self.basepath, ["todo"], seen)
        ensureDirectoryExists(self.basepath, ["todo"], seen)
        self.assertEqual(seen,
                        set([os.path.join(self.basepath, "todo")]))
        self.assertEqual(os.listdir(self.basepath), ["todo"])

    def testNestedPathAdd(self):
        seen=set()
        ensureDirectoryExists(self.basepath, ["grandpa", "father", "son"], seen)
        self.assertEqual(seen,
                set([os.path.join(self.basepath, "grandpa", "father", "son")]))

    def testNestedPathWrongOrder(self):
        seen=set()
        ensureDirectoryExists(self.basepath, ["father", "son"], seen)
        ensureDirectoryExists(self.basepath, ["father"], seen)
        self.assertEqual(seen,
                set([os.path.join(self.basepath, "father", "son"),
                     os.path.join(self.basepath, "father")]))

