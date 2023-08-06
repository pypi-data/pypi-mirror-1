from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='redturtle.munin',
      version=version,
      description="Munin plugins for zope/plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: ZODB",
        "Framework :: Zope2",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope munin',
      author='Andrew Mleczko',
      author_email='andrew.mleczko@redturtle.it',
      url='http://www.redturtle.it',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'gocept.munin',
          'threadframe',          
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
