import operator
import os
import shutil
import tempfile
import types
from unittest import TestCase
from odfsvn.package import ODFPackage
from odfsvn.package import UnpackedODFPackage
from odfsvn.package import ZipODFPackage

data_path = os.path.join(os.path.dirname(__file__), "data")
testdir_path = os.path.join(data_path, "test.odt")
testfile_path = os.path.join(data_path, "testfile.odt")


class MockPackage(ODFPackage):
    def __init__(self, data=None):
        if data is None:
            self.data={}
        else:
            self.data=data

    def keys(self):
        for key in self.data.keys():
            yield key

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key]=value


class ODFPackageTests(TestCase):
    def testLength(self):
        odf=MockPackage()
        self.assertEqual(len(odf), 0)
        odf.data["one"]=1
        self.assertEqual(len(odf), 1)
        odf.data["two"]=2
        self.assertEqual(len(odf), 2)

    def testNonZero(self):
        odf=MockPackage()
        self.assertEqual(bool(odf), False)
        odf.data[False]=False
        self.assertEqual(bool(odf), True)

    def testKeys(self):
        odf=MockPackage()
        keys=odf.keys()
        self.failUnless(isinstance(keys, types.GeneratorType))
        self.assertEqual(list(keys), [])
        odf.data["one"]=1
        self.assertEqual(list(odf.keys()), ["one"])

    def testValues(self):
        odf=MockPackage()
        values=odf.values()
        self.failUnless(isinstance(values, types.GeneratorType))
        self.assertEqual(list(values), [])
        odf.data["one"]=1
        self.assertEqual(list(odf.values()), [1])


class GenericPackageTests:
    def testKeys(self):
        keys=self.odf.keys()
        self.failUnless(isinstance(keys, types.GeneratorType))
        self.assertEqual(set(keys),
                         set(["content.xml", "meta.xml", "mimetype",
                             "settings.xml", "styles.xml",
                             "META-INF/manifest.xml",
                             "Thumbnails/thumbnail.png"]))

    def testHasKey(self):
        self.assertEqual(self.odf.has_key("oops.xml"), False)
        self.assertEqual(self.odf.has_key("meta.xml"), True)

    def testNestedHasKey(self):
        self.assertEqual(self.odf.has_key("META-INF/oops.xml"), False)
        self.assertEqual(self.odf.has_key("META-INF/manifest.xml"), True)

    def testContains(self):
        self.assertEqual("oops.xml" in self.odf, False)
        self.assertEqual("meta.xml" in self.odf, True)

    def testNestedContains(self):
        self.assertEqual("META-INF/oops.xml" in self.odf, False)
        self.assertEqual("META-INF/manifest.xml" in self.odf, True)

    def testGetItem(self):
        data=self.odf["meta.xml"]
        self.failUnless("office:document-meta" in data)

    def testNestedGetItem(self):
        data=self.odf["META-INF/manifest.xml"]
        self.failUnless("manifest:manifest" in data)

    def testGetItemWrongKey(self):
        self.assertRaises(KeyError, operator.getitem, self.odf, "oops.xml")

    def testAddItem(self):
        self.odf["new.txt"]="Test item"
        self.failUnless("new.txt" in self.odf)
        self.failUnless("new.txt" in list(self.odf.keys()))
        self.assertEqual(self.odf["new.txt"], "Test item")

    def testRemoveItem(self):
        del self.odf["meta.xml"]
        self.failUnless("meta.xml" not in self.odf)
        self.failUnless("meta.xml" not in list(self.odf.keys()))
        self.assertRaises(KeyError, operator.getitem, self.odf, "meta.xml")

    def testRemoveUnknownItemRaises(self):
        self.assertRaises(KeyError, operator.delitem, self.odf, "not-here")

    def testAddRemovedItem(self):
        del self.odf["meta.xml"]
        self.odf["meta.xml"]="Test item"
        self.failUnless("meta.xml" in self.odf)
        self.failUnless("meta.xml" in list(self.odf.keys()))
        self.assertEqual(self.odf["meta.xml"], "Test item")



class UnpackedODFPackageTests(TestCase, GenericPackageTests):
    def setUp(self):
        self.newpath=tempfile.mktemp(suffix=".odt")
        shutil.copytree(testdir_path, self.newpath)
        self.odf=UnpackedODFPackage(self.newpath)

    def tearDown(self):
        shutil.rmtree(self.newpath)

    def testInvalidPath(self):
        self.assertRaises(ValueError, UnpackedODFPackage, "/i-do-not-exist")

    def testFilePath(self):
        self.assertRaises(ValueError, UnpackedODFPackage, testfile_path)

    def testDirectGetPath(self):
        self.assertEqual(self.odf._getpath("meta.xml"),
                os.path.join(self.newpath, "meta.xml"))

    def testNestedGetPath(self):
        self.assertEqual(self.odf._getpath("META-INF/manifest.xml"),
                os.path.join(self.newpath, "META-INF", "manifest.xml"))
        self.assertEqual(self.odf._getpath("META-INF/manifest.xml"),
                os.path.join(self.newpath, "META-INF", "manifest.xml"))

    def testGetItemDirectory(self):
        self.assertRaises(KeyError, operator.getitem, self.odf, "META-INF")


class ZipODFPackageTests(TestCase, GenericPackageTests):
    def setUp(self):
        self.newpath=tempfile.mktemp(suffix=".odt")
        shutil.copyfile(testfile_path, self.newpath)
        self.odf=ZipODFPackage(self.newpath)

    def tearDown(self):
        self.odf.close()
        os.unlink(self.newpath)

    def testInvalidPath(self):
        self.assertRaises(IOError, ZipODFPackage, "/i/do/not/exist")

    def testDirectoryPath(self):
        self.assertRaises(IOError, ZipODFPackage, testdir_path)

    def testDoNotLeaveEmptyDroppings(self):
        path=tempfile.mktemp(suffix=".odt")
        odf=ZipODFPackage(path, mode="w")
        odf.close()
        del odf
        self.failIf(os.path.exists(path))


class MetadataTests(TestCase):
    def setUp(self):
        self.odf=MockPackage()

    def testNoMetadata(self):
        self.odf.data["meta.xml"]="<root/>"
        self.assertEqual(self.odf.getRepositoryInfo(), {})

    def testIgnoreNonRepositoryInfo(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
             <meta:user-defined meta:name="Info 1"></meta:user-defined>
            </root>"""
        self.assertEqual(self.odf.getRepositoryInfo(), {})

    def testRepositoryInfo(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
             <meta:user-defined meta:name="Repository-one">1</meta:user-defined>
             <meta:user-defined meta:name="Repository-two">2</meta:user-defined>
            </root>"""
        self.assertEqual(self.odf.getRepositoryInfo(), {"one" : "1", "two" : "2"})

    def testCorrectNamespaceOnly(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
             <user-defined meta:name="Repository-foo">bar</user-defined>
            </root>"""
        self.assertEqual(self.odf.getRepositoryInfo(), {})

    def testDefaultTypeIsSvn(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
             <meta:user-defined meta:name="Repository-URL"></meta:user-defined>
            </root>"""
        self.assertEqual(self.odf.getRepositoryInfo()["type"], "svn")

    def testDefaultTypeNotSetWithoutURL(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0">
             <meta:user-defined meta:name="Repository-foo">bar</meta:user-defined>
            </root>"""
        self.failUnless("type" not in self.odf.getRepositoryInfo())

    def testSetNothing(self):
        self.odf.data["meta.xml"]="<root/>"
        self.odf.setRepositoryInfo({})
        self.failUnless(u"Repository" not in self.odf.data["meta.xml"])

    def testSetRemovesOldData(self):
        self.odf.data["meta.xml"]=\
            """<?xml version="1.0" encoding="UTF-8"?>
            <root xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
                  xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0">
             <office:meta>
              <meta:user-defined meta:name="Repository-URL"></meta:user-defined>
             </office:meta>
            </root>"""
        self.odf.setRepositoryInfo({})
        self.failUnless(u"Repository" not in self.odf.data["meta.xml"])

    def testNamespaceDeclared(self):
        self.odf.data["meta.xml"]="<root/>"
        self.odf.setRepositoryInfo(dict(uuid="two"))
        self.failUnless(u"xmlns:meta" in self.odf.data["meta.xml"])

    def testSetURL(self):
        self.odf.data["meta.xml"]="<root/>"
        self.odf.setRepositoryInfo(dict(uuid="two"))
        self.failUnless(u"meta:user-defined" in self.odf.data["meta.xml"])
        self.failUnless(u"Repository-UUID" in self.odf.data["meta.xml"])
        self.failUnless(u"two" in self.odf.data["meta.xml"])


