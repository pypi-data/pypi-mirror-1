haufe.releaser
==============

``haufe.releaser`` is a command extension for ``setuptools`` and is intended
as a setuptools frontend for interacting with ``haufe.eggserver``.

Installation
------------

Use easy_install::

    easy_install haufe.releaser

Usage
-----

``haufe.releaser`` provides a new command **local_upload** to be used together
with setuptools. It works in the same way as the standard **upload** command however 
it uploads your distributions to a locale haufe.eggserver.

Example::

   python2.4 setup.py sdist bdist_egg local_upload

You can specify a custom egg server URL using the  ``--eggserver <URL>`` option:

   python2.4 setup.py sdist bdist_egg local_upload --eggserver http://somehost:8080/myeggs

