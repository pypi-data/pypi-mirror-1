import errno
import os
import shutil
import tempfile
import zipfile
from xml.dom import minidom


def getXmlInfo(node, tag, attr=None):
    """Retrieve data from a XML DOM.

    Normally this will retrieve the contents of the first element with
    the given tagname. If attr is also specific the value of that
    attribute on the found element will be returned instead.
    """
    elements=node.getElementsByTagName(tag)
    if not elements:
        raise KeyError, tag

    element=elements[0]
    if attr is None:
        return "".join([child.data for child in element.childNodes
                        if child.nodeType==node.TEXT_NODE])
    else:
        return element.getAttribute(attr)


def expandXML(source, encoding="utf-8"):
    """Expand a XML text so allow svn to merge changes.

    ODF packages tend to use a single line for the entire XML data. This
    makes it impossible for subversion to merge changes during updates.
    This method expands the XML over multiple lines.
    """
    if isinstance(source, basestring):
        source=minidom.parseString(source)
    return source.toprettyxml(indent="  ", newl="\n", encoding=encoding)


def ensureDirectoryExists(base, path, seen_paths=None):
    """Ensure a directory, including all parent directories, exists.

    seen_paths is a set of pathnames that have been checked before.
    This can be used to optimise calls.
    """

    if seen_paths is None:
        seen_paths=set([base])

    path=os.path.join(base, *path)
    if path not in seen_paths:
        seen_paths.add(path)
        try:
            os.makedirs(path)
        except OSError, e:
            if e.errno!=errno.EEXIST:
                raise 


def unpack(filename, directory=None):
    """Unpack a zip file.

    If not destiniation directory is given a new directory is created.
    This method returns a tuple with the directory path and the list
    of files unpacked.
    """
    if directory is None:
        directory=tempfile.mkdtemp()

    zip=zipfile.ZipFile(filename, "r")
    seen_paths=set([directory])

    files=[]
    for file in zip.namelist():
        if file.endswith("/"):
            continue
        
        parts=file.split("/")
        path=file.split("/")[:-1]
        ensureDirectoryExists(directory, path, seen_paths)

        path=os.path.join(*([directory]+parts))
        output=open(path, "wb")
        output.write(zip.read(file))
        output.close()
        files.append(file)

    return (directory, files)


def withTempDirectory(func):
    """Function decorator for functions which require a temporary directory.

    This will add a named parameter 'tempdir' to the method invocation which
    contains the absolute path for the temporary directory. This directory and
    its contents will be removed after the function completes.

    If a tempdir parameter is passed in explicitly this will be used instead.
    """
    def wrapper(*args, **kwargs):
        if "tempdir" in kwargs:
            return func(*args, **kwargs)

        kwargs["tempdir"]=tempfile.mkdtemp()
        try:
            return func(*args, **kwargs)
        finally:
            shutil.rmtree(kwargs["tempdir"])

    return wrapper

