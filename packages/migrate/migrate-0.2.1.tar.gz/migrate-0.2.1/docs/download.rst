=======
Migrate
=======

Download
========

Migrate builds on SQLAlchemy_, so you should install that first. 

You can get Migrate from the `cheese shop`_, or via easy_install_::

 easy_install migrate

You should now be able to use the *migrate* command from the command line::

 migrate

This should list all available commands. *migrate help COMMAND* will display more information about each command. 

.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall#installing-easy-install
.. _sqlalchemy: http://www.sqlalchemy.org/download.myt
.. _`cheese shop`: http://www.python.org/pypi/migrate

Development
===========

Migrate's Subversion_ repository is at http://erosson.com/migrate/svn/

To get the latest trunk::

 svn co http://erosson.com/migrate/svn/migrate/trunk

Patches should be submitted via Trac tickets.

.. _subversion: http://subversion.tigris.org/
