from setuptools import setup, find_packages

name = "plone.recipe.zope2zeoserver"
version = '0.6'

setup(
    name = name,
    version = version,
    author = "Hanno Schlichting",
    author_email = "plone@hannosch.info",
    description = "ZC Buildout recipe for installing a Zope 2 zeo server",
    long_description = open("README.txt").read(),
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
