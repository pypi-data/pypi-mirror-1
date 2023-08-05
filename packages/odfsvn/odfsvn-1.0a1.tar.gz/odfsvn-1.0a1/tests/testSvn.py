import os
import pwd
import shutil
import tempfile
from unittest import TestCase
from odfsvn.svn import run
from odfsvn.svn import SVNException
from odfsvn.svn import SVNRepository
from odfsvn.package import UnpackedODFPackage
from odfsvn.package import ZipODFPackage

data_path = os.path.join(os.path.dirname(__file__), "data")
testdir_path = os.path.join(data_path, "test.odt")
testfile_path = os.path.join(data_path, "testfile.odt")

def copytree(src, dst):
    names = os.listdir(src)
    os.mkdir(dst)
    for name in names:
        if name.startswith("."):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
        except (IOError, os.error), why:
            print "Can't copy %s to %s: %s" % (`srcname`, `dstname`, str(why))

class runTests(TestCase):
    def testUnknownCommand(self):
        self.assertRaises(SVNException, run, "idonotexist")

    def testCommandError(self):
        # Windows has no 'false' command so this will be an unknown command
        # test there.
        self.assertRaises(SVNException, run, "false")

    def testCommandSuccess(self):
        run("echo")

    def testCommandOutput(self):
        output=run("echo", "Hello, world!")
        self.assertEqual(output.read().strip(), "Hello, world!")


class SVNRepositoryTests(TestCase):
    def setUp(self):
        self.basepath=tempfile.mkdtemp()
        self.svnodfpath=os.path.join(self.basepath, "odfsvn")
        self.odf=UnpackedODFPackage(self.svnodfpath, mode="w")
        self.repopath=os.path.join(self.basepath, "repo")
        self.repouri="file://" + self.repopath
        run("svnadmin", "create", self.repopath)
        run("svn", "mkdir", "-m", "test commit",
                os.path.join(self.repouri, "test"))
        run("svn", "mkdir", "-m", "test commit",
                os.path.join(self.repouri, "test.odt"))
        run("svn", "import", "-m" "add test odt", testdir_path,
                self.repouri+os.sep+"test.odt"+os.path.sep+"trunk")
        self.repo=SVNRepository(self.repouri+os.sep+"test.odt")

    def tearDown(self):
        shutil.rmtree(self.basepath)

    def testInfoReturnsCachedData(self):
        marker=[]
        self.repo._info=marker
        self.failUnless(self.repo.info is marker)
        self.failUnless(self.repo._info is marker)

    def testGetInfoFromPathSetsCache(self):
        self.failIf(hasattr(self.repo, "_info"))
        self.repo._getInfoFromPath(self.repouri)
        self.failUnless(hasattr(self.repo, "_info"))

    def testGetInfoFromPath(self):
        self.repo._getInfoFromPath(self.repouri)
        self.assertEqual(self.repo._info["type"], "svn")
        self.assertEqual(self.repo._info["url"], self.repouri+os.path.sep+"test.odt")
        self.assertEqual(self.repo._info["author"],
                        pwd.getpwuid(os.getuid())[0])
        self.assertEqual(self.repo._info["revision"], 3)

    def testInvalidUri(self):
        repo=SVNRepository(self.repouri+os.sep+"test")
        try:
            repo.retrieve(None)
        except SVNException, e:
            pass
        else:
            self.fail()

    def testRetrieveGetsAllFiles(self):
        self.repo.retrieve(self.odf)
        info=self.odf.getRepositoryInfo()
        self.assertEqual(set(self.odf.keys()),
                         set(["content.xml", "meta.xml", "mimetype",
                             "settings.xml", "styles.xml",
                             "META-INF/manifest.xml",
                             "Thumbnails/thumbnail.png"]))

    def testRetrieveMetadata(self):
        self.repo.retrieve(self.odf)
        info=self.odf.getRepositoryInfo()
        self.assertEqual(info["uuid"], self.repo.info["uuid"])
        self.assertEqual(info["revision"], self.repo.info["revision"])
        self.assertEqual(info["url"], self.repo.info["url"])

    def testStoreCreatesSvnStructure(self):
        path=os.path.join(self.basepath, "store.odt")
        shutil.copyfile(testfile_path, path)
        odf=ZipODFPackage(path)
        repo=SVNRepository(self.repouri+os.sep+"store.odt")
        repo.store(odf)

        output=run("svn", "ls", self.repouri+os.sep+"store.odt")
        output=output.read()
        output=set(output.strip().split("\n"))
        self.assertEqual(output, set(["tags/", "trunk/",]))

    def testStoreAddsAllFiles(self):
        path=os.path.join(self.basepath, "store.odt")
        shutil.copyfile(testfile_path, path)
        odf=ZipODFPackage(path)
        repo=SVNRepository(self.repouri+os.sep+"store.odt")
        repo.store(odf)

        output=run("svn", "ls", "-R", self.repouri+os.sep+"store.odt"+os.sep+"trunk")
        output=output.read()
        output=set(output.strip().split("\n"))
        self.assertEqual(output, set(["META-INF/",
                                      "META-INF/manifest.xml",
                                      "Thumbnails/",
                                      "Thumbnails/thumbnail.png",
                                      "content.xml",
                                      "meta.xml",
                                      "mimetype",
                                      "settings.xml",
                                      "styles.xml",]))

    def testDefaultCommitMessage(self):
        path=os.path.join(self.basepath, "store.odt")
        shutil.copyfile(testfile_path, path)
        odf=ZipODFPackage(path)
        repo=SVNRepository(self.repouri+os.sep+"store.odt")
        repo.store(odf)

# XXX test if retrieving a bad url does not leave an empty ODF behind
