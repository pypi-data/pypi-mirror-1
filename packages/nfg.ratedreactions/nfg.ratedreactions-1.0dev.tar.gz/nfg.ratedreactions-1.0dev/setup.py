from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='nfg.ratedreactions',
      version=version,
      description="A zope3 product to add rated reactions to (plone) content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone ratings',
      author='NFG Net Facilities Group BV',
      author_email='support@nfg.nl',
      url='http://www.nfg.nl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.lead == 1.0',
          'five.intid == 0.4.2',
          'pysqlite == 2.5.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
