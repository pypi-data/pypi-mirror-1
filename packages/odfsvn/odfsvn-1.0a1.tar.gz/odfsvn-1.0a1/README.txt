.. contents::

Introduction
============

ODFSVN is a set of tools that allow you to manage ODF_ documents in
a subversion_ repository. There are several reasons that make this a
very useful thing to do:

* it allows you to use all features of a version control system: all
  changes are archived along with change notes, making it possible
  to roll back to previous versions, see who made what changes and why,
  etc.

* it makes it possible to have multiple people sharing their changes
  to a document through a shared repository. That means that you
  can always see all changes from all editors, update your version
  to the latest revision and submit your changes. No matter where you
  are, with or without access to your email, you will always be
  able to share your work.

For now this can be done through the ``odfsvn`` command line tool. In the
(near) future this will also be possible through a plugin for
`OpenOffice.org`_.

.. _ODF: http://en.wikipedia.org/wiki/OpenDocument
.. _subversion: http://subversion.tigris.org/
.. _OpenOffice.org: http://www.openoffice.org/


Quick example
=============

Suppose you are working on a proposal with a group of people. The proposal
is stored in a file called ``proposal.odt`` which you have just created.
The first thing that you need to do is import this file into an existing
repository::

   $ odfsvn import -m "Simplon proposal for odf RFP" proposal.odt \
     http://code.simplon.biz/proposals/odf.odt
   Commited revision 22

This will have added your file to the repository. The ``-m`` parameter
was used to set the commit message for this change.

You can now use the *info* command to check the repository information
inside your file::
   
   $ odfsvn info proposal.odt
   Path: proposal.odt
   Type: svn
   URL: http://code.simplon.biz/proposals/odf.odt
   Repository UUID: 1a87ecf8-a9bc-47a4-9dc9-5f45153203cc
   Revision: 22

If one of your co-editors wants to work on this proposal he must first
retrieve the document using the *checkout* command::

   $ odfsvn checkout http://code.simplon.biz/proposals/odf.odt
   Checked out revision 22

He can now edit the ``odf.odt`` file using his normal editors. After
making any changes he can commit them using the *commit* command::

   $ odfsvn commit -m "Added estimates and initial planning" odf.odt
   Changes committed.

You can now update your local copy using the *update* command::

   $ odfsvn update proposal.dt
   Updated to revision 23


