import errno
import md5
import os
import shutil
import tempfile
import zipfile
from xml.dom import minidom
from xml.dom import XMLNS_NAMESPACE
from odfsvn import NS_META
from odfsvn import NS_OFFICE
from odfsvn.utils import expandXML

# A list of the python and XML names of the revision metadata we handle.
# In the XML all names are prefixed with 'Revision-' as well.
metadata_names = [
        ( "type",     "Type",     unicode),
        ( "uuid",     "UUID",     unicode),
        ( "revision", "Revision", int),
        ( "url",      "URL",      unicode),
        ]

def XmlToPython(name, value):
    for (p,x,t) in metadata_names:
        if x==name:
            return (p, t(value))
    else:
        raise KeyError, name

def PythonToXml(name):
    for (p,x,t) in metadata_names:
        if p==name:
            return x
    else:
        raise KeyError, name


class ODFPackage(object):
    """A ODF package abstraction.

    This provides a dict-like interface for a ODF package. This makes it
    possible to list, access and update all files in a ODF package without
    having to know if it is zipped, unpacked or in a repository.

    In order to optimise performance where possible generators are used
    instead of lists.
    """
    def __del__(self):
        self.close()

    def close(self):
        return

    def values(self):
        for file in self.keys():
            yield self[file]

    def items(self):
        for file in self.keys():
            yield (file, self[file])

    def __len__(self):
        return len(list(self.keys()))

    def __nonzero__(self):
        # This may look odd, but it deals efficiently with generators returned
        # by self.keys().
        for i in self.keys():
            return True
        return False


    def getRepositoryInfo(self):
        """Extract the repository metadata from a package.

        The information is returned as a dictionary.
        """
        info={}
        dom=minidom.parseString(self["meta.xml"])
        for element in dom.getElementsByTagNameNS(NS_META, u"user-defined"):
            name=element.getAttributeNS(NS_META, u"name")
            if not name.startswith(u"Repository-"):
                continue
            name=name[11:]
            text="".join([child.data for child in element.childNodes
                            if child.nodeType==element.TEXT_NODE])
            text=text.strip()
            try:
                (key, value)=XmlToPython(name, text)
                info[key]=value
            except KeyError:
                info[name]=text

        if "url" in info and "type" not in info:
            info["type"]="svn"

        return info


    def clearRepositoryInfo(self):
        """Remove all repository information from this ODF."""
        self.setRepositoryInfo({})


    def setRepositoryInfo(self, info):
        """Update the repository information in a package."""

        def addNode(dom, parent, name, value):
            node=dom.createElementNS(NS_META, u"meta:user-defined")
            node.setAttributeNS(NS_META, u"meta:name", u"Repository-"+name)
            node.appendChild(dom.createTextNode(str(value)))
            parent.appendChild(node)

        dom=minidom.parseString(self["meta.xml"])
        root=dom.documentElement

        ns=root.getAttributeNS(XMLNS_NAMESPACE, "meta")
        if not ns:
            root.setAttributeNS(XMLNS_NAMESPACE, "xmlns:meta", NS_META)

        meta=root.getElementsByTagNameNS(NS_OFFICE, u"meta")
        if not meta:
            meta=dom.createElementNS(NS_OFFICE, u"office:meta")
            root.appendChild(meta)
        else:
            meta=meta[0]

        for element in meta.getElementsByTagNameNS(NS_META, u"user-defined"):
            name=element.getAttributeNS(NS_META, u"name")
            if name.startswith(u"Repository-"):
                meta.removeChild(element)

        for (key, value) in info.items():
            try:
                key=PythonToXml(key)
            except KeyError:
                continue
            addNode(dom, meta, key, value)

        self["meta.xml"]=expandXML(dom)

        dom.unlink()



class UnpackedODFPackage(ODFPackage):
    """An unpacked ODF package."""

    def __init__(self, path, mode="a"):
        if mode=="w":
            if os.path.isdir(path):
                raise ValueError, "Path already exists"
            os.mkdir(path)
        else:
            if not os.path.isdir(path):
                raise ValueError, "Not a directory: %s" % path
        self.readonly=(mode=="r")
        self.path=path

        if mode!="w" and "meta.xml" not in self:
            raise ValueError, "'%s' is not a valid ODF package" % path

    def _getpath(self, key):
        return os.path.join(self.path, key.replace("/", os.path.sep))

    def keys(self):
        prefix=len(self.path)

        for (dirpath, dirnames, filenames) in os.walk(self.path):
            if ".svn" in dirnames:
                dirnames.remove(".svn")
            dirpath=dirpath[prefix:]
            dirpath=dirpath.replace(os.path.sep, "/") + "/"
            if dirpath.startswith("/"):
                dirpath=dirpath[1:]

            for file in filenames:
                yield dirpath+file

    def has_key(self, key):
        return os.path.isfile(self._getpath(key))

    __contains__ = has_key


    def __delitem__(self, key):
        if self.readonly:
            raise TypeError, "Can not modify a read-only package"
        try:
            os.unlink(self._getpath(key))
        except OSError, e:
            if e.errno in (errno.ENOENT, errno.EISDIR):
                raise KeyError, key
            raise

    def __getitem__(self, key):
        try:
            return open(self._getpath(key)).read()
        except IOError, e:
            if e.errno in (errno.ENOENT, errno.EISDIR):
                raise KeyError, key
            raise

    def __setitem__(self, key, value):
        if self.readonly:
            raise TypeError, "Can not modify a read-only package"
        path=self._getpath(key)
        try:
            os.makedirs(os.path.dirname(path))
        except OSError, e:
            if e.errno!=errno.EEXIST:
                raise 
        open(path, "w").write(value)



class ZipODFPackage(ODFPackage):
    """A standard zipped ODF package."""

    def __init__(self, path, mode="a"):
        self.readonly=False
        self.mode=mode
        if mode=="w":
            self.zip=None
        else:
            self.zip=zipfile.ZipFile(path, mode)
        self.readonly=(mode=="r")
        self.path=path
        self.tempdir=None
        self.changed=set()
        self.removed=set()

        if mode!="w" and "meta.xml" not in self:
            raise ValueError, "'%s' is not a valid ODF package" % path


    def _tempPath(self, key):
        if self.tempdir is None:
            self.tempdir=tempfile.mkdtemp()

        return os.path.join(self.tempdir,
                md5.new(key).hexdigest())


    def close(self):
        if getattr(self, "tempdir", None) is None:
            return

        current=set(self.keys())

        changed=self.changed.intersection(current)
        new=self.changed.difference(current)

        if not changed:
            # Only new files, we can just append those to our zip and be done.
            for key in self.changed:
                self.zip.write(self._tempPath(key),
                        compress_type=zipfile.ZIP_DEFLATED)
        else:
            newpath=self.path+".new"
            fd=os.open(newpath, os.O_EXCL|os.O_CREAT|os.O_WRONLY)
            newfile=os.fdopen(fd, "w")
            newzip=zipfile.ZipFile(newfile, "w", zipfile.ZIP_DEFLATED)

            persist=current.difference(changed).difference(new)
            assert len(changed)+len(new)+len(persist)==len(current)
            for path in persist:
                newzip.writestr(path, self.zip.read(path))
            for path in changed:
                newzip.write(self._tempPath(path), path)

            newzip.close()
            os.unlink(self.path)
            os.rename(newpath, self.path)

        shutil.rmtree(self.tempdir)
        self.tempdir=None
        self.zip.close()


    def keys(self):
        for entry in self.changed:
            yield entry

        for file in self.zip.namelist():
            if file.endswith("/") or file in self.removed or file in self.changed:
                continue
            yield file


    def has_key(self, key):
        if self.zip is None:
            return False
        if key in self.removed:
            return False
        if key in self.changed:
            return True
        try:
            self.zip.getinfo(key)
        except KeyError:
            return False
        else:
            return True

    __contains__ = has_key

    def __delitem__(self, key):
        if self.readonly:
            raise TypeError, "Can not modify a read-only package"
        if key not in self:
            raise KeyError, key
        self.changed.discard(key)
        self.removed.add(key)


    def __getitem__(self, key):
        if self.zip is None:
            return False
        if key in self.removed:
            raise KeyError, key

        if key in self.changed:
            return open(self._tempPath(key)).read()

        return self.zip.read(key)


    def __setitem__(self, key, value):
        if self.readonly:
            raise TypeError, "Can not modify a read-only package"

        # ZIP requires CP-437/ISO-8859-1 filenames
        assert isinstance(key, str) 

        if self.zip is None:
            self.zip=zipfile.ZipFile(path, mode)

        file=open(self._tempPath(key), "w")
        file.write(value)
        file.close()

        self.removed.discard(key)
        self.changed.add(key)

__all__ = [ "ZipODFPackage", "UnpackedODFPackage" ]

