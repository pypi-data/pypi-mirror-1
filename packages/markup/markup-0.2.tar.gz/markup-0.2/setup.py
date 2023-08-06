from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='markup',
      version=version,
      description="generate HTML markup programmatically",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='http://www.openplans.org/people/k0s/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
