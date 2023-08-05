from odfsvn.package import ZipODFPackage
from odfsvn.svn import SVNRepository
from odfsvn.svn import SVNException
import sys
import optparse

aliases = {
        "ci"      : "commit",
        "co"      : "checkout",
        "up"      : "update",
        }
options = None

def ActionInfo(args):
    """Show repository information for a ODF document.

    Usage:
       odfsvn info <file>
    """
    if len(args)!=1:
        raise hell

    odf=ZipODFPackage(args[0], "r")
    info=odf.getRepositoryInfo()
    if "type" not in info:
        print >>sys.stderr, "'%s' has no repository information" % args[0]
        sys.exit(1)
    print "Path: %s" % args[0]
    print "Type: %s" % info["type"]
    if info["url"].endswith("/trunk"):
        print "URL: %s" % info["url"][:-6]
    else:
        parts=info["url"].split("/")
        print "URL: %s" % "/".join(parts[:-2])
        print "Tag: %s" % parts[-1]
    print "Repository UUID: %s" % info["uuid"]
    print "Revision: %s" % info["revision"]



def ActionImport(args):
    """Import an ODF document in a subversion repository.
    
    Usage:
        odfsvn import <file> <repository URL>

    For example to import the file 'presentation.odf' into a repository
    you can run this command:

        odfsvn presentation.odf http://svn.example.com/2007/movies.odf
    """
    if len(args)!=2:
        raise hell
    (path, url)=args

    odf=ZipODFPackage(path, "r")
    repo=SVNRepository(url)
    repo.store(odf, message=options.message)


def ActionCheckout(args):
    """Retrieve a document from a repository.

    Usage:
       odfsvn checkout <url> [<filename>]

    If you do not specify a filename the last part of the repository
    URL will be used.

    Example:

        odfsvn checkout http://svn.example.com/2007/movies.odf
    """
    if len(args)==1:
        url=args[0]
        path=url.split("/")[-1]
    elif len(args)==2:
        (url, path)=args
    else:
        raise hell

    repo=SVNRepository(url)
    odf=ZipODFPackage(path, "w")
    tag=getattr(options, "tag")
    repo.retrieve(odf, revision=getattr(options, "revision"), tag=tag)
    if tag:
        print "Checked out tag %s revision %d" % (tag, repo.info["revision"])
    else:
        print "Checked out revision %d" % repo.info["revision"]


def ActionCommit(args):
    """Comment changes to a document.

    Usage:
        odfsvn commit <filename>
    """
    if len(args)!=1:
        raise hell
    odf=ZipODFPackage(args[0], "a")
    repo=SVNRepository(odf.getRepositoryInfo()["url"])
    repo.commit(odf, message=options.message)
    print "Changes commited."


def ActionUpdate(args):
    """Update a document to the current svn version.

    Usage:
        odfsvn update <filename>
    """
    if len(args)!=1:
        raise hell

    odf=ZipODFPackage(args[0], "a")
    repo=SVNRepository(odf.getRepositoryInfo()["url"])
    repo.update(odf)
    print "Updated to revision %d" % repo.info["revision"]


def ActionHelp(args):
    """Show detailed information about an action.
    
    Usage:
        odfsvn help <command>
    """

    if len(args)==0:
        args=["help"]
    elif len(args)!=1:
        raise hell

    args[0]=aliases.get(args[0], args[0])
    handler=globals().get("Action"+args[0].capitalize())
    if handler is None:
        print >>sys.stderr, "Unknown command: %s" % args[0]
        sys.exit(1)

    print handler.__doc__.replace("\n    ", "\n")


class HelpFormatter(optparse.IndentedHelpFormatter):
    def format_description(self, description):
        return description


def main():
    global options

    parser=optparse.OptionParser(
            formatter=HelpFormatter(),
            usage="%prog [options] <action> [<parameters>]",
            description="Manage ODF documents maintained in a subversion repository.\n"
                        "Available actions are:\n"
                        "\n"
                        "   help        Show detailed information about an action\n"
                        "   info        Show repository information for a document\n"
                        "   import      Import a document into a repository\n"
                        "   checkout    Retrieve a document from a repository\n"
                        "   commit      Commit changes to the repository\n"
                        "   update      Update a document to the latest repository version\n")
    parser.add_option("-t", "--tag", action="store", dest="tag",
            help="Use this tag instead of trunk")
    parser.add_option("-r", "--revision", action="store", dest="revision",
            help="Checkout a specific revision")
    parser.add_option("-m", "--message", action="store", dest="message",
            help="Log message for this action")
    parser.add_option("-v", "--verbose", action="count", dest="verbose",
            help="Be more verbose about what is happening")

    parser.set_defaults(verbose=0,
                        message="ODSVN commit")
    (options,args)=parser.parse_args(values=options)

    if not args:
        parser.error("No action specified")

    args[0]=aliases.get(args[0], args[0])
    handler=globals().get("Action"+args[0].capitalize())
    if handler is None:
        parser.error("Unknown action '%s'" % args[0])

    try:
        handler(args[1:])
    except SVNException, e:
        print >>sys.stderr, "SVN error: %s" % str(e)
        sys.exit(1)
    except IOError, e:
        print >>sys.stderr, str(e)
        sys.exit(1)


if __name__=="__main__":
    main()

