Copyright (c) 2008, Infrae. All rights reserved.
See also LICENSE.txt

Silva Membership support for PluggableAuthService
-------------------------------------------------

This package provides a new PluggableAuthService (PAS) extension,
which let Silva users be valid PAS users. This can be used to restrain
access to users which already have a Silva member object.

This extension require at least `Silva`_ 2.0.7 or higher.

Installation
------------

If you installed Silva using buildout, by getting one from the `Infrae
SVN`_ repository, or creating one using `Paster`_, you should edit your
buildout configuration file ``buildout.cfg`` to add or edit the
following section::

  [instance]

  eggs = ... 
        silva.pas.membership

  zcml = ...
        silva.pas.membership

If the section ``instance`` wasn't already in the configuration file,
pay attention to re-copy values for ``eggs`` and ``zcml`` from the
profile you use.

After you can restart buildout::

  $ ./bin/buildout


If you don't use buildout, you can install this extension using
``easy_install``, and after create a file called
``silva.pas.membership-configure.zcml`` in the
``/path/to/instance/etc/package-includes`` directory.  This file will
responsible to load the extension and should only contain this::

  <include package="silva.pas.membership" />


Latest version
--------------

The latest version is available in a `Subversion repository
<https://svn.infrae.com/silva.pas.membership/trunk#egg=silva.pas.membership-dev>`_.


.. _Infrae SVN: https://svn.infrae.com/buildout/silva/
.. _Paster: https://svn.infrae.com/buildout/silva/INSTALL.txt
.. _Silva: http://infrae.com/products/silva


