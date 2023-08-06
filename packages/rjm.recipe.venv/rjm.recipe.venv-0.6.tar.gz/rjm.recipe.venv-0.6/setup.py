# -*- coding: utf-8 -*-
"""
This module contains the setup configuration for rjm.recipe.venv.
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join('.', *rnames)).read()

version = '0.6'
entry_point = 'rjm.recipe.venv:Venv'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='rjm.recipe.venv',
      version=version,
      description="zc.buildout recipe to turn the entire buildout tree into a virtualenv",
      long_description=read('README.txt'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        ],
      keywords='buildout virtualenv',
      author='Rob Miller',
      author_email='rob@kalistra.com',
      url='http://www.bitbucket.org/rafrombrc/rjm.recipe.venv',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rjm', 'rjm.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        'virtualenv',
                        ],
      entry_points=entry_points,
      )

