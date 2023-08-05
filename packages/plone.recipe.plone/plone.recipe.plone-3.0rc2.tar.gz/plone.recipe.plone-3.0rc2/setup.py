from setuptools import setup, find_packages
import sys, os

name = "plone.recipe.plone"

version = '3.0rc2'

setup(name=name,
      version=version,
      description="Install Plone",
      long_description="""\
This recipe allows you to install Plone, based on the packages used for the
Plone installers.

Here is an example buildout::

    [buildout]
    parts = plone zope2 instance
    eggs =
    develop = 

    [plone]
    recipe = plone.recipe.plone

    [zope2]
    recipe = plone.recipe.zope2install
    url = ${plone:zope2-url}

    [instance]
    recipe = plone.recipe.zope2instance
    zope2-location = ${zope2:location}
    user = admin:admin
    http-port = 8080
    debug-mode = on
    verbose-security = on
    eggs =
        ${buildout:eggs}
        ${plone:eggs}
    zcml = 

    products =
        ${plone:products}
        ${buildout:directory}/products

Notice how the 'plone' recipe is able to supply a URL for a "known good" 
version of Zope (you can of course choose not to use it). 

The 'instance' recipe is configured with two parameters set by the 'plone'
recipe:

 plone:eggs -- The various Plone eggs
 
 plone:products -- A directory containing the Plone Zope 2 products

Other possible options in the 'plone' section include:

 eggs -- Override the eggs used by Plone. If you specify an egg here that is
    also part of the standard Plone distribution, the specified egg will 
    override the default. For example, if you want to track svn for a 
    particular egg, check it out to the src/ directory, add a line to
    'develop' in buildout (e.g. "develop = src/plone.theme" to track the
    plone.theme package) and then add "eggs = plone.theme" to the 'plone'
    section. Alternatively, if you need to upgrade or downgrade a particular
    egg, you can do so with a version specification.
    
 find-links -- Specify one or more find-links for setuptools to download
    eggs from. By default, this includes http://dist.plone.org and any
    find-links specified in the main [buildout] section.
 
 urls -- A list of URLs to download packages from, overriding those from the
    installer configuration. You can use the options 'nested-packages' and
    'version-suffix-packages' to give the names of download archives which
    contain a parent directory and the actual product in a sub directory,
    and products which when extracted have a directory containing the version
    number. See plone.recipe.distros for more information.
    
 zope2-url -- Override the Zope 2 URL from the installer (not that there is
    much point in doing so).
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Framework :: Buildout",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Programming Language :: Python",
          ],
      keywords='',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/collective/buildout/plone.recipe.plone',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires = [
        'zc.buildout', 
        'setuptools', 
        'zc.recipe.egg',
        'plone.recipe.distros'
      ],
      dependency_links = [
        'http://download.zope.org/distribution/'
      ],
      entry_points = {
        'zc.buildout': ['default = %s:Recipe' % name]},
      )
