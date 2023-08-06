from setuptools import setup, find_packages
import os

version = open('jyu/pathkey/version.txt').read().strip('\n')

setup(name='jyu.pathkey',
      version=version,
      description="Restricts access to Plone content without proper pathkey",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='jyu.pathkey pathkey restrict',
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@jyu.fi',
      url='http://svn.plone.org/svn/collective/jyu.pathkey',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jyu'],
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
