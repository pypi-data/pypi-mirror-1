from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='rpatterson.stripdupes',
      version=version,
      description="Strip duplicated sequences of lines from within files",
      long_description=
      open(os.path.join(
          "rpatterson", "stripdupes", "README.txt")).read() + '\n\n' +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Ross Patterson',
      author_email='me@rpatterson.net',
      url='http://pypi.python.org/pypi/rpatterson.stripdupes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rpatterson'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'rpatterson.listfile',
      ],
      extras_require=dict(test=['zope.testing']),
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      stripdupes = rpatterson.stripdupes:main
      """,
      )
