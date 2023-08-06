from setuptools import setup, find_packages

version = '2.0.9'
name='collective.recipe.zmysqlda'
setup(name=name,
      version=version,
      description="Recipe for installing ZMySQLDA",
      long_description="""\
collective.recipe.zmysqlda is simple recipe used for installing ZMySQLDA from 
the source tarball. 
ZMySQLDA 2.0.8 tarball has internal structure lib/python/Products/ZMySQLDA/.... 
and if you need it in your instance, you must extract it manually.
This buildout recipe solves this problem.

Example::

  [zmysqlda]
  recipe = collective.recipe.zmysqlda
  target = ${buildout:directory}/products

**target** is optional. Defaults to *${buildout:directory}/products*

Please note, you need MySQL-python egg in your buildout.cfg or 
mysql-python package installed in your python instance.

2.0.9
=====
Fixed buildout['download-directory']

2.0.8
=====
Initial release
""",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='buildout',
      author='Radim Novotny',
      author_email='radim.novotny@corenet.cz',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.zmysqlda',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
	  install_requires = ['zc.buildout', 'setuptools'],
      entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
      )
