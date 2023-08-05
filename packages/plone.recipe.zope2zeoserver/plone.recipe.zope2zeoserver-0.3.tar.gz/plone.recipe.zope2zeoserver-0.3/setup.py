from setuptools import setup, find_packages

name = "plone.recipe.zope2zeoserver"
version = '0.3'

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "plone@hannosch.info",
    description = "ZC Buildout recipe for installing a Zope 2 zeo server",
          long_description="""\
This recipe creates and configures a Zope 2 ZEO server in parts. It also
installs a control script, which is like zeoctl, in the bin/ directory.
The name of the control script is the the name of the part in buildout.

You can use it with a part like this::

  [zeoserver]
  recipe = plone.recipe.zope2zeoserver
  zope2-location = /path/to/zope2/install
  zeo-address = 8100

The available options are:

 zope2-location -- The path where Zope 2 is installed. If you are also
  using the plone.recipe.zope2install recipe, and you have that configured
  as a part called 'zope2' prior to the zope2instance part, you can use
  ${zope2:location} for this parameter.
  
 zeopack -- The path to the zeopack.py backup script. A wrapper for this will 
  be generated in bin/zeopack, which sets up the appropriate environment to
  run this. Defaults to "${zope2-location}/utilities/ZODBTools/zeopack.py".
  Set this option to an empty value if you do not want this script to be 
  generated.
  
 zeo-conf -- A relative or absolute path to a zeo.conf file. If this is
  not given, a zope.conf will be generated based on the the options below.
  
The following options all affect the generated zope.conf.
  
 zeo-address -- Give a port for the ZEO server. Defaults to 8100.
  
 zeo-log -- The filename of the ZEO log file. Defaults to 
  var/log/${partname}.log

 file-storage -- The filename where the ZODB data file will be stored. 
  Defaults to var/filestorage/Data.fs.
  
 zope-conf-additional -- Give additional lines to zope.conf. Make sure you
  indent any lines aftter the one with the parameter.           
""",
    license = "ZPL 2.1",
    keywords = "zope2 buildout",
    url='https://svn.plone.org/svn/plone/ploneout/trunk/src/'+name,
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Zope2",
      "Programming Language :: Python",
      ],
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['plone', 'plone.recipe'],
    install_requires = ['zc.buildout', 'setuptools', 'zc.recipe.egg'],
    dependency_links = ['http://download.zope.org/distribution/'],
    zip_safe=False,
    entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
    )
