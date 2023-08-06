from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='ooo2tools.daemon',
      version=version,
      description="scan a directory, looking for pyUno instructions added by some program to execute them",
      long_description="""\
scan a specified directory. This daemon expects to find tasks created in a define way by some program. tasks contain documents and sequences of instructions as defined in ooo2tools.core""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='open office daemon',
      author='Alexandre LE GROS',
      author_email='alexandre_lg@hotmail.fr',
      url='',
      license='',
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
