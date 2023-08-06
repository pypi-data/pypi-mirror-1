from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.kss.inlinejs',
      version=version,
      description="Plugin that allows you to put javascript code evaluated by kss",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='kss plugin',
      author='Davide Moro',
      author_email='davide.moro@redomino.com',
      url='http://www.redomino.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.kss'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'kss.core'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
