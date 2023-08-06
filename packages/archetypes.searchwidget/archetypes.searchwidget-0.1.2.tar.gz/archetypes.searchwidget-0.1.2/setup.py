from setuptools import setup, find_packages
import os

version = '0.1.2'

setup(name='archetypes.searchwidget',
      version=version,
      description="",
      long_description = open(os.path.join("src", "archetypes", "searchwidget", "README.txt")).read() + '\n\n' +
                         open(os.path.join("src", "archetypes", "searchwidget", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone archtypes widget search reference',
      author='Rok Garbas',
      author_email='rok.garbas@gmail.com',
      url='http://svn.plone.org/svn/archetypes/MoreiFieldAndWidgets',
      license='GPL',
      packages = find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['archetypes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.searchtool',
          'collective.jqueryui',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
