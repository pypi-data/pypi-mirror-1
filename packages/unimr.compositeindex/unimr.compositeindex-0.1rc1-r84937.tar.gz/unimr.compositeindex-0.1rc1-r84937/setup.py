from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='unimr.compositeindex',
      version=version,
      description="Composite index for the Catalog",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Catalog ZCatalog Composite Index',
      author='Andreas Gabriel',
      author_email='gabriel@hrz.uni-marburg.de',
      url='https://svn.plone.org/svn/collective/unimr.compositeindex',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['unimr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.monkeypatcher',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
