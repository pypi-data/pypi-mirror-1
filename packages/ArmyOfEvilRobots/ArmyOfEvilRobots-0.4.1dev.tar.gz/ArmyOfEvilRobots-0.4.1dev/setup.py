from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

setup(name='ArmyOfEvilRobots',
      version=version,
      description="Utility library. Contains per app cross platform config library tools for now.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Derek Anderson',
      author_email='derek@armyofevilrobots.com',
      url='http://www.armyofevilrobots.com/',
      license='MIT',
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
