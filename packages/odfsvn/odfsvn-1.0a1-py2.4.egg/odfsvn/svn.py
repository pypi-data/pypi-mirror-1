import errno
import os
import subprocess
from xml.dom import minidom
from odfsvn.package import UnpackedODFPackage
from odfsvn.utils import withTempDirectory
from odfsvn.utils import expandXML
from odfsvn.utils import getXmlInfo

class SVNException(Exception):
    """SubVersioN exception"""


def run(*command):
# XXX This will need to be updated to run correctly on Windows under py2exe
# See http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions
    try:
        process=subprocess.Popen(command,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError, e:
        if e.errno==errno.ENOENT:
            raise SVNException("Command not found: '%s'" % command[0])
        raise

    stderr=process.stderr.read()
    exitcode=process.wait()
    if exitcode!=0:
        raise SVNException(stderr)
    return process.stdout


class SVNRepository:
    def __init__(self, url):
        self.url=url


    def _getInfoFromPath(self, path):
        command=["svn", "info", "--non-interactive", "--xml", path]
        process=subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        errors=process.stderr.read().strip()
        exitcode=process.wait()
        if exitcode!=0:
            raise SVNException(process.stderr.read())

        xml=process.communicate()[0]
        dom=minidom.parseString(xml)
        entries=dom.getElementsByTagName("entry")
        if not entries:
            raise SVNException(errors)

        root=entries[0]
        try:
            self._info=dict(
                    type="svn",
                    url=self.url,
                    root=getXmlInfo(root, "root"),
                    uuid=getXmlInfo(root, "uuid"),
                    author=getXmlInfo(root, "author"),
                    revision=int(getXmlInfo(root, "commit", "revision")),
                    )
        except KeyError:
            raise SVNException("Not a valid repository")


    @property
    def info(self):
        if not hasattr(self, "_info"):
            self._getInfoFromPath(self.url)
        return self._info


    @withTempDirectory
    def retrieve(self, odf, revision=None, tag=None, tempdir=None):
        if tag is None:
            url=self.url+"/trunk"
        else:
            url=self.url+"/tags/"+tag

        if revision is None:
            run("svn", "co", "--quiet", "--non-interactive", url, tempdir)
        else:
            run("svn", "co", "--quiet", "--non-interactive",
                    "--revision", revision, url, tempdir)

        if not os.path.isfile(os.path.join(tempdir, "meta.xml")):
            raise SVNException("Not an ODF document")

        for (dirpath, dirnames, filenames) in os.walk(tempdir):
            if ".svn" in dirnames:
                dirnames.remove(".svn")
            odfpath=dirpath[len(tempdir):].replace(os.path.sep, "/")
            if odfpath.startswith("/"):
                odfpath=odfpath[1:]
            if odfpath:
                odfpath+='/'
            for file in filenames:
                odf[odfpath+file]=open(os.path.join(dirpath, file)).read()

        info=self.info
        info["url"]=url
        odf.setRepositoryInfo(self.info)


    @withTempDirectory
    def store(self, odf, odf_update=True, message="ODFSVN commit", tempdir=None):
        """Store an ODF package in the repository.

        If odf_update is true the repository information in the ODF
        packge will be updated.
        """

        parts=self.url.split("/")
        parent="/".join(parts[:-1])
        filename=parts[-1]

        run("svn", "co", "--quiet", "--non-interactive",
                "--non-recursive", parent, tempdir)

        odfdir=os.path.join(tempdir, filename)

        run("svn", "mkdir", odfdir)
        run("svn", "mkdir", os.path.join(odfdir, "tags"))

        unpacker=UnpackedODFPackage(os.path.join(odfdir, "trunk"), "w")
        for (path, data) in odf.items():
            unpacker[path]=data
        unpacker.clearRepositoryInfo()
        
        run("svn", "add", "--quiet", os.path.join(odfdir, "trunk"))
        run("svn", "ci", "--quiet", "--non-interactive",
                "--message", message, tempdir)


    @withTempDirectory
    def commit(self, odf, odf_update=True, message="ODFSVN commit", tempdir=None):
        """Commit changes to the repository."""
        self.update(odf, tempdir=tempdir)
        run("svn", "ci", "--quiet", "--non-interactive",
                "--message", message, tempdir)


    @withTempDirectory
    def update(self, odf, tempdir=None):
        """Merge updated from the repository in an ODF."""
        info=odf.getRepositoryInfo()
        if info.get("type")!="svn":
            raise TypeError("SVNRepository can not handle non-svn ODF packages")
        if info.get("url")!=self.url:
            raise ValueError("ODF from foreign repository given")
        if info["uuid"]!=self.info["uuid"]:
            raise SVNException("ODF repository has a different UUID")

        run("svn", "co", "--quiet", "--non-interactive",
                "--revision", info["revision"], self.url, tempdir)

        svnodf=UnpackedODFPackage(tempdir)
        for (key,data) in odf.items():
            svnodf[key]=data
        svnodf.close()

        output=run("svn", "up", "--non-interactive", tempdir)
        output=output.read().split("\n")
        if not output[-1]:
            output=output[:-1]
        output=[line.rstrip().split(None, 1) for line in output[:-1]]
        prefix=tempdir+os.path.sep
        output=[(action[0], path.replace(prefix,""))
                        for (action,path) in output]

        if 'C' in [action for (action,path) in output]:
            raise SVNException("Conflict during update")

        for (action, path) in output:
            if action in ('A', 'U', 'G'):
                odf[path]=svnodf[path]
            elif action=='D':
                del odf[path]

        odf.setRepositoryInfo(self.info)

