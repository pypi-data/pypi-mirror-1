This file is for you to describe the relmanweb application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``relmanweb_console`` using easy_install::

    easy_install relmanweb_console

If you don't already have it, this will install releasemanager as well.  ReleaseManager will install a script called relman_ctl.  The format for the
command is as described in the README for ReleaseManager, except that now, the
added option of webconsole has been created.  If you intend to install the
webconsole, simply type the following:

    relman_ctl generate webconsole -a admin

This will install the webconsole with the admin-only authentication plugin.

Simply go into the directory that's created, and run 

    paster serve development.ini

from the command line.  This should start a default Pylons instance running
the ReleaseManager WebConsole.
