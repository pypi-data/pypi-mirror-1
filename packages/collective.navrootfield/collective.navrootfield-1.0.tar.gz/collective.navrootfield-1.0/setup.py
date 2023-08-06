from setuptools import setup, find_packages
import os

version = '1.0'
readme = open("README.txt").read()
setup(name='collective.navrootfield',
      version=version,
      description="",
      long_description=readme[readme.find('\n\n'):] + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Florian Schulze',
      author_email='florian.schulze@gmx.net',
      url='http://svn.plone.org/svn/collective/collective.navrootfield',
      license='GPL',
      packages=['collective', 'collective.navrootfield'],
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
