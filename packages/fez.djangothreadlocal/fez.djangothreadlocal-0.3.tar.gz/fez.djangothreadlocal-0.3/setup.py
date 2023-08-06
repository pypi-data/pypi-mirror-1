from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='fez.djangothreadlocal',
      version=version,
      description="Add the user object to Django threadlocals",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License"
        ],
      keywords='',
      author='Dan Fairs',
      author_email='dan@fezconsulting.com',
      url='http://www.fezconsulting.com',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fez'],
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
