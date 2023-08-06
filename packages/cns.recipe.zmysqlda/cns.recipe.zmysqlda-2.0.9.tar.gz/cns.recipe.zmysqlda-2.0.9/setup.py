from setuptools import setup, find_packages

version = '2.0.9'
name='cns.recipe.zmysqlda'
setup(name=name,
      version=version,
      description="Recipe for installing ZMySQLDA",
      long_description="""\
cns.recipe.zmysqlda is simple recipe used for installing ZMySQLDA from tarball. ZMySQLDA 2.0.8 tarball
has structure lib/python/Products/ZMySQLDA/.... and has to be extraceted manually.

Example::

  [zmysqlda]
  recipe = cns.recipe.zmysqlda
  target = ${buildout:directory}/products

**target** is optional. Defaults to *${buildout:directory}/products* 

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
      url='http://corenet-int.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cns', 'cns.recipe'],
      include_package_data=True,
      zip_safe=False,
	  install_requires = ['zc.buildout', 'setuptools'],
      entry_points = {'zc.buildout':
                    ['default = %s:Recipe' % name]},
      )
