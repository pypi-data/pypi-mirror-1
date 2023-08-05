from setuptools import setup, find_packages
import sys, os

version = '0.5.1'

setup(name='topp.build.lib',
      version=version,
      description="buildit library for topp",
      long_description="""
a library used to build TOPP software.  this includes
commands, tasks, and other generic library components.
""",
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords='',
      author='The Open Planning Project',
      author_email='info@openplans.org',
      url='http://openplans.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'skel']),
      namespace_packages=['topp', 'topp.build'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'workingenv.py==dev,>=0.6.6',
          'buildit',
          'PoachEggs',
          'topp.utils>0.1',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      create-deployment = topp.build.lib.create_skeleton:main
      """,      
      dependency_links=[
        "http://www.openplans.org/projects/opencore/dependencies"
        ],
      )
