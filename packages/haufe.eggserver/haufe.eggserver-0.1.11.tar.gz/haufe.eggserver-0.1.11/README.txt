haufe.eggserver
---------------

``haufe.eggserver`` is a tiny webfront to a local egg/sourcecode archive
distribution directory (eggs and other distribution files stored directly on
the filesystem).

It currently supports basic browsing through a local distribution 
directory on the filesystem and basic upload support for eggs and source
code distributions (requires ``haufe.releaser``).  It supports out-of-the-box
infinite repository directories.


Installation
============

- download the source code archive and unpack it
- run ``buildout``
- start the instance using ``bin/zopectl start``
- add an eggserver application instance through the management interface
- use the ``edit`` view for configuring the path to your local
  distribution directory and the visible title of your instance
  (Login with username ``admin`` and password ``123``)

Dependencies
============

- ``zc.buildout`` (use easy_install for installing zc.buildout)
- ``Grok`` (will be installed automatically when using ``zc.buildout``)
- ``gocept.cache`` (willl be install automatically when using ``zc.buildout``)
- ``haufe.releaser`` (use easy_install for install haufe.releaser)

Uploading packages
==================

You have to choices:

- use ``haufe.releaser`` and its ``local_upload`` command

- use the standard setuptools ``upload`` command:

  python2.4 setup.py sdist upload -r http://localhost:8080/eggs


Things ``haufe.eggserver`` won't do
===================================

Since ``haufe.eggserver`` is not designed as a full-fledged PyPI replacement,
there are some things that the implementation will not do right do (and possibly
will not do):

- no dedicated security model (everyone is trused and allowed to upload packages). Keep in 
  mind that ``haufe.eggserver`` is basically designed for company/project internal usage

Author
======

``haufe.eggserver`` was written by Andreas Jung for Haufe Mediengruppe, Freiburg, Germany
and ZOPYX Ltd. & Co. KG, Tuebingen, Germany.


License
=======

``haufe.eggserver`` is licensed under the Zope Public License 2.1.

See the included ZPL.txt file.


Contact
=======

| ZOPYX Ltd. & Co. KG
| Andreas Jung
| Charlottenstr. 37/1
| D-72070 Tuebingen, Germany
| E-mail: info at zopyx dot com
| Web: http://www.zopyx.com


