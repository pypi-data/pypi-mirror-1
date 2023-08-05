try:
    from zope.interface import Interface
except ImportError:
    class Interface:
        pass

class IODFPackage(Interface):
    """A ODF package abstraction.

    This provides a dict-like interface for a ODF package. This makes it
    possible to list, access and update all files in a ODF package without
    having to know if it is zipped, unpacked or in a repository.

    In order to optimise performance where possible generators are used
    instead of lists.
    """

    def close():
        """Commit all changes and close the package.

        It is an error to access the package after calling this method.
        """

    def values():
        """Return the contents of all files in the package."""

    def items():
        """Return an iterable over (path, contents) tuples."""

    def __len__():
        """Return the number of files in the package."""

    def __nonzero__():
        """Test if the package is empty."""

    def getRepositoryInfo():
        """Extract the repository metadata from a package.

        The information is returned as a dictionary.
        """

    def setRepositoryInfo(info):
        """Update the repository information in a package."""


class IRepository(Interface):
    def __init__(uri):
        """Initialize a repository located at URI."""

    def UUID():
        """Return the UUID for the repository."""

    def retrieve(path, odf):
        """Retrieve an ODF package from the path inside the repository
        and store it in an existing ODF package."""

    def store(path, odf, odf_update=True, message=None):
        """Store an ODF package in the repository.

        If odf_update is true the repository information in the ODF
        packge will be updated.
        """

