from setuptools import setup, find_packages

versionfile = open('version.txt')
version = versionfile.read().strip()
versionfile.close()

setup(name='collective.recipe.mxzopeda',
      version=version,
      description="A buildout recipe to install eGenix mx.ODBC.ZopeDA and a licence",
      long_description=open("README.txt").read() + "\n" +
                      open("HISTORY.txt").read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Framework :: Buildout",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='build mx.ODBC mx.ODBC ZopeDA',
      author='Zest Software, Jarn',
      author_email='info@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.mxzopeda',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = collective.recipe.mxzopeda:Recipe
      """,
      )
