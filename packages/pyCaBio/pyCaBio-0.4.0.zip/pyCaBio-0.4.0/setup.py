#!/usr/bin/env python

from setuptools import setup

setup(name='pyCaBio',
      version='0.4.0',
      description='caBIO Python API',
      long_description='Pythonic API for the caBIO Database based on web services',
      license='caBIG Open Source Software License',
      platforms='All',
      author='Konrad Rokicki',
      author_email='rokickik@mail.nih.gov',
      url='http://cabioapi.nci.nih.gov/',
      packages=[
            'cabig',
            'cabig.cabio',
            'cabig.cabio.common',
            'cabig.cabio.common.provenance',
      ],
      install_requires=['pyCaCORE==0.2.0'],
      namespace_packages = ['cabig'],
      dependency_links = [
            'https://gforge.nci.nih.gov/frs/download.php/4655/pyCaCORE-0.2.0-py2.5.egg'
      ],
      test_suite = 'tests.unit_tests'
     )
