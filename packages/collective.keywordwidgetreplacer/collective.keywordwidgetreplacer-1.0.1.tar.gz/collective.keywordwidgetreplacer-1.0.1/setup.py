from setuptools import setup, find_packages
import os

version = open(os.path.join("collective", "keywordwidgetreplacer", "version.txt")).read().strip()

setup(name='collective.keywordwidgetreplacer',
      version=version,
      description="Replace that annoying KeywordWidget with the much more helpful AddRemoveWidget!",
      long_description=open(os.path.join("collective", "keywordwidgetreplacer", "README.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Archetypes KeywordWidget',
      author='Michael Dunlap',
      author_email='dunlapm@u.washington.edu',
      url='http://plone.org/products/keywordwidgetreplacer',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          'Products.AddRemoveWidget',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
