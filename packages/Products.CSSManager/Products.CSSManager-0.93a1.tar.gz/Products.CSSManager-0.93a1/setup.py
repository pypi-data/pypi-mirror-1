from setuptools import setup, find_packages
import os

version = '0.93'

setup(name='Products.CSSManager',
      version=version,
      description="CSSManager is a simple add-on for managing CSS properties exposed by Plone 3 and 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='WebLion group at Penn State University',
      author_email='webmaster@weblion.psu.edu',
      url='https://weblion.psu.edu/svn/weblion/weblion/Products.CSSManager',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
