from setuptools import setup, find_packages
import sys, os

version = '0.5.1'

# add a dav client to update dep links?

setup(name='topp.build.opencore',
      version=version,
      description="buildit builder for the opencore softwar",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='build topp openplans',
      author='whit',
      author_email='jhammel@openplans.org',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['topp', 'topp.build'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['topp.build.lib>=0.5'], 
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      build-opencore = topp.build.opencore:main
      """,
      dependency_links=["http://www.openplans.org/projects/opencore/dependencies"],
      )
      
