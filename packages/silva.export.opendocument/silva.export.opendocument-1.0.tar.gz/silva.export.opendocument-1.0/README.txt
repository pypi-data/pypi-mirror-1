Copyright (c) 2008, Infrae. All rights reserved.
See also LICENSE.txt

Silva OpenDocument Export
-------------------------

This extension provides an export feature to ODT (Open Document Format)
for `Silva`_ 2.1 and higher, for Silva Publication and Silva Document.


Installation
------------

If you installed Silva using buildout, by getting one from the `Infrae
SVN`_ repository, or creating one using `Paster`_, you should edit your
buildout configuration file ``buildout.cfg`` to add or edit the
following section::

  [instance]

  eggs +=
     silva.export.opendocument

  zcml +=
     silva.export.opendocument


After you can re-run buildout::

  $ ./bin/buildout


If you don't use buildout, you can install this extension using
``easy_install``, and after create a file called
``silva.export.opendocument-configure.zcml`` in the
``/path/to/instance/etc/package-includes`` directory.  This file will
be responsible to load the extension and should only contain this::

  <include package="silva.export.opendocument" />


Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/silva.export.opendocument/trunk#egg=silva.export.opendocument>`_.

.. _Infrae SVN: https://svn.infrae.com/buildout/silva/
.. _Paster: https://svn.infrae.com/buildout/silva/INSTALL.txt
.. _Silva: http://infrae.com/products/silva
