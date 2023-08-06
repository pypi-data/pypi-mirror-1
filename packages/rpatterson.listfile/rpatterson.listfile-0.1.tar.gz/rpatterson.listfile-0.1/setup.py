from setuptools import setup, find_packages
import os

version = '0.1'

tests_require = ['zope.testing']

setup(name='rpatterson.listfile',
      version=version,
      description="Support list operations over lines of file-like objects",
      long_description=
      open(os.path.join(
          "rpatterson", "listfile", "README.txt")).read() + '\n\n' +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/rpatterson.listfile',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rpatterson'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      test_suite = "rpatterson.mailsync.tests.test_suite",
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
