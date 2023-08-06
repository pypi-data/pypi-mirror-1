#!/usr/bin/env python

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages


from setuptools import setup

setup(name='HadoopCalculator',
      version='1.0',
      description='Hadoop Calculator - Providing an educated guess for performance of your Hadoop cluster',
      author='Jon Miller',
      author_email='jonEbird@gmail.com',
      url='http://cloud.github.com/downloads/jonEbird/Hadoop-Utils/hadoop_calculator.py',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Topic :: System',
        'Topic :: Utilities',
        ],
      packages = ['hadoopcalculator'],
      scripts = ['scripts/hadoop_calculator'],
     )
