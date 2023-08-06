from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='rum.component',
      version=version,
      description="Lightweight Component Architecture",
      long_description="""\
""",
      classifiers=['Development Status :: 3 - Alpha',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Component rum',
      author='Alberto Valverde, Michael Brickenstein',
      author_email='brickenstein@mfo.de',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "setuptools"
      ],
      entry_points="""
      # -*- Entry points: -*-
      # These are just for the tests
      [test.robot.weapon]
      axe = rumcomponent.tests.test_component:Axe
      """,
      )
