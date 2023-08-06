from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='prdg.zope.permissions',
      version=version,
      description="An user-friendlier API for roles and permissions on Zope.",
      long_description='\n'.join([
        open('README.txt').read(),
        open('TODO.txt').read(),
        open('HISTORY.txt').read(),                
      ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope zope2 permissions security',
      author='Rafael Oliveira',
      author_email='rafaelbco@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['prdg'],
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
