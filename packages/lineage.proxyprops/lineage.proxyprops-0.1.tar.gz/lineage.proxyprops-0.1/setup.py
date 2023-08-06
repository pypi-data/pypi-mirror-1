from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='lineage.proxyprops',
      version=version,
      description="Small wrapper package to add support for collective.proxyprops",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("lineage","proxyprops","README.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Six Feet Up, Inc.',
      author_email='info@sixfeetup.com',
      url='http://svn.plone.org/svn/collective/lineage.proxyprops',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['lineage'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.lineage',
          'collective.proxyproperties'
      ],
      entry_points="",
      )
