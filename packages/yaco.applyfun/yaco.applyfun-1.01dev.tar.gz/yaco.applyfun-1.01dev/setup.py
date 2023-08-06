from setuptools import setup, find_packages
import os

version = '1.01'

setup(name='yaco.applyfun',
      version=version,
      description="Apply functions to objects in the ZODB",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Yaco S.L.',
      author_email='eperez@yaco.es',
      url='http://www.yaco.es',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['yaco'],
      package_data={
          '':['*.zcml',
              '*.txt',
              'i18n/*.po',
              'i18n/*.pot',
              'templates/*.pt']
          },
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
