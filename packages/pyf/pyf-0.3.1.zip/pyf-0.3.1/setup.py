from setuptools import setup, find_packages
import sys, os

version = '0.3.1'

setup(name='pyf',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules',
                   'Development Status :: 4 - Beta'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jonathan Schemoul, Florent Aide, Jerome Collette',
      author_email='jonathan.schemoul@gmail.com, florent.aide@gmail.com, collette.jerome@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "pyjon.utils"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
