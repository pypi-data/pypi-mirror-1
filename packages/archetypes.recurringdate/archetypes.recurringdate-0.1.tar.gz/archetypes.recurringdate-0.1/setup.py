from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='archetypes.recurringdate',
      version=version,
      description="Field/Widget to support recurring dates.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        ],
      keywords='date recurring archetypes field widget',
      author='Dorneles Tremea',
      author_email='dorneles@tremea.com',
      url='http://dev.plone.org/archetypes/log/MoreFieldsAndWidgets/archetypes.recurringdate',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['archetypes'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'python-dateutil',
          'p4a.common',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
