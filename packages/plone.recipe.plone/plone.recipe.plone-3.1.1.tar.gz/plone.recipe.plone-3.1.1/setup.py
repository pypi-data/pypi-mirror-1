from setuptools import setup, find_packages

name = "plone.recipe.plone"

version = '3.1.1'

setup(name=name,
      version=version,
      description="Install Plone",
      long_description=open("README.txt").read(),
      classifiers=[
          "License :: OSI Approved :: Zope Public License",
          "Framework :: Plone",
          "Programming Language :: Python",
          ],
      keywords='',
      author='Martin Aspeli',
      author_email='optilude@gmx.net',
      url='http://svn.plone.org/svn/plone/dist/plone.recipe.plone',
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
