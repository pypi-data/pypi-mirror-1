from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='teamrubber.pdberrorlog',
      version=version,
      description="Allows a nice interface to the Plone error log from ztc functional tests",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone pdb unittest',
      author='Matthew Wilkes',
      author_email='matt.wilkes@teamrubber.com',
      url='http://teamrubber.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['teamrubber'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      tests_require=[
        'setuptools',
        'nose',
      ],
      test_suite="nose.collector",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
