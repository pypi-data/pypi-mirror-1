plone.recipe.zope2zeoserver
===========================

This recipe creates and configures a Zope 2 ZEO server in parts. It also
installs a control script, which is like zeoctl, in the bin/ directory.
The name of the control script is the the name of the part in buildout.

You can use it with a part like this::

  [zeoserver]
  recipe = plone.recipe.zope2zeoserver
  zope2-location = /path/to/zope2/install
  zeo-address = 8100

Options
-------

zope2-location
  The path where Zope 2 is installed. If you are also using the
  plone.recipe.zope2install recipe, and you have that configured as a part
  called 'zope2' prior to the zope2instance part, you can use
  ${zope2:location} for this parameter.

zeopack
  The path to the zeopack.py backup script. A wrapper for this will be
  generated in bin/zeopack, which sets up the appropriate environment to
  run this. Defaults to "${zope2-location}/utilities/ZODBTools/zeopack.py".
  Set this option to an empty value if you do not want this script to be 
  generated.

zeo-conf
  A relative or absolute path to a zeo.conf file. If this is not given, a
  zeo.conf will be generated based on the the options below.

The following options all affect the generated zope.conf.

zeo-address
  Give a port for the ZEO server. Defaults to 8100.

effective-user
  The name of the effective user for the ZEO process. Defaults to not setting
  an effective user.

invalidation-queue-size
  The invalidation-queue-size used for the ZEO server. Defaults to 100.

zeo-log
  The filename of the ZEO log file. Defaults to var/log/${partname}.log

storage-number
  The number used to identify a storage.

file-storage
  The filename where the ZODB data file will be stored. 
  Defaults to var/filestorage/Data.fs.

blob-storage
  The folder where the ZODB blob data files will be stored.

socket-name
  The filename where ZEO will write its socket file.
  Defaults to var/zeo.zdsock.

zeo-conf-additional
  Give additional lines to zeo.conf. Make sure you indent any lines after
  the one with the parameter.           

Reporting bugs or asking questions
----------------------------------

We have a shared bugtracker and help desk on Launchpad:
https://bugs.launchpad.net/collective.buildout/
