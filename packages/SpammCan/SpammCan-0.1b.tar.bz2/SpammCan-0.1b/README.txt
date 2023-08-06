SpammCan
========

:Author: Christopher Arndt
:Version: 0.1b
:Date: 2008-11-10
:Description: A simple pastbin built on TurboGears and Pygments.

.. contents::
  :depth: 1

General Information
-------------------

SpammCan is yet another pastbin web application. It distinguishes itself from
its competitors by the following features:

* Has syntax highlighting support for over 100 languages thanks to the use of
  Pygments_.

* Is easy to install thanks to setuptools_.

* Uses large, random GUIDs for paste entries in its URLs instead of sequential
  paste numbers to discourage spammers.

  Also detects and rejects spamming attempts with the help of a SpamBayes_
  filter.

* Is built on TurboGears_ 1.1, Genshi_, and SQLAlchemy_.

* Uses a SQLite database by default, but can use any database system supported
  by SQLAlchemy and TurboGears.


Getting the Code
----------------

You can run your own SpammCan server! For more information, downloads, and
source code, visit the project home page at

    http://chrisarndt.de/projects/SpammCan

You can also install SpammCan via its Python Package Index (aka Cheeseshop_)
entry_::

    $ [sudo] easy_install SpammCan

Finally, if you want the latest development code for SpammCan, you can check it
out from the Subversion repository::

    $ svn co svn://chrisarndt.de/projects/SpammCan/trunk SpammCan

.. _cheeseshop: http://pypi.python.org/
.. _entry: http://pypi.python.org/pypi/SpammCan
.. _pygments: http://pygments.pocoo.org/
.. _turbogears: http://www.turbogears.org/
.. _setuptools: http://pypi.python.org/pypi/setuptools
.. _spambayes: http://spambayes.sourceforge.net/
.. _genshi: http://genshi.edgewall.org/
.. _sqlalchemy: http://sqlalchemy.org/



.. include:: TODO.txt

.. include:: CHANGELOG.txt
