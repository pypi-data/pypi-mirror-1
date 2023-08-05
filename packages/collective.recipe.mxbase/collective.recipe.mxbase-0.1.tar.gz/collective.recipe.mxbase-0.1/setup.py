import os
from setuptools import setup, find_packages

name = "collective.recipe.mxbase"
version = '0.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = name,
      version = version,
      description = "A buildout recipe to install eGenix mx.base (mx.DateTime, mx.TextTools...)",
      long_description=(read('README.txt')),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Framework :: Buildout",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='build mx.Base',
      author='Jean-Francois Roche',
      author_email='jfroche@affinitic.be',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.mxbase',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points = {'zc.buildout': ['default = %s:Recipe' % name]},
      )
